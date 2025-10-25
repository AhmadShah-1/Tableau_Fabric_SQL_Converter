"""
Regex-based remapping helpers for Tableau → Microsoft Fabric (T-SQL) conversion.

This module centralizes conservative, order-aware regex transforms for common
Tableau patterns. It is designed to be used as a preprocessing step before or
after token-based conversion.

Notes:
- Transforms are conservative and try to avoid breaking valid SQL. When an
  automatic rewrite is ambiguous, the function returns the input unchanged and
  records a flag for manual review.
- For bracketed identifiers (e.g. [field]) we normalize to bare identifiers to
  make subsequent regex and token rules easier to match consistently.
"""

import re
from typing import List, Tuple, Optional, Dict


Flag = Tuple[int, str]  # (line_number, reason)


class RegexRemapper:
    def __init__(self, varchar_default_len: int = 20) -> None:
        self.varchar_default_len = varchar_default_len

        # Precompiled patterns used across remaps
        self.re_bracket_ident = re.compile(r"\[([^\]]+)\]")
        self.re_if = re.compile(r"\bIF\s*\(", re.IGNORECASE)
        self.re_ifnull = re.compile(r"\bIFNULL\s*\(", re.IGNORECASE)
        self.re_true = re.compile(r"\bTRUE\b", re.IGNORECASE)
        self.re_false = re.compile(r"\bFALSE\b", re.IGNORECASE)
        self.re_comment_slashes = re.compile(r"//")
        self.re_now = re.compile(r"\bNOW\s*\(\s*\)", re.IGNORECASE)
        self.re_today = re.compile(r"\bTODAY\s*\(\s*\)", re.IGNORECASE)
        self.re_length = re.compile(r"\bLENGTH\s*\(", re.IGNORECASE)
        self.re_substr = re.compile(r"\bSUBSTR\s*\(", re.IGNORECASE)
        self.re_makedate = re.compile(r"\bMAKEDATE\s*\(", re.IGNORECASE)
        self.re_makedatetime = re.compile(r"\bMAKEDATETIME\s*\(", re.IGNORECASE)
        self.re_ln = re.compile(r"\bLN\s*\(", re.IGNORECASE)
        self.re_log = re.compile(r"\bLOG\s*\(", re.IGNORECASE)
        self.re_int = re.compile(r"\bINT\s*\(\s*([^\)]+?)\s*\)", re.IGNORECASE)
        self.re_str = re.compile(r"\bSTR\s*\(\s*([^\)]+?)\s*\)", re.IGNORECASE)
        self.re_float = re.compile(r"\bFLOAT\s*\(\s*([^\)]+?)\s*\)", re.IGNORECASE)
        self.re_date_cast = re.compile(r"\bDATE\s*\(\s*([^\)]+?)\s*\)", re.IGNORECASE)
        self.re_split = re.compile(r"\bSPLIT\s*\(\s*([^,]+?)\s*,\s*'([^']*)'\s*,\s*(\d+)\s*\)", re.IGNORECASE)
        self.re_startswith = re.compile(r"\bSTARTSWITH\s*\(\s*([^,]+?)\s*,\s*'([^']*)'\s*\)", re.IGNORECASE)
        self.re_endswith = re.compile(r"\bENDSWITH\s*\(\s*([^,]+?)\s*,\s*'([^']*)'\s*\)", re.IGNORECASE)
        self.re_contains = re.compile(r"\bCONTAINS\s*\(\s*([^,]+?)\s*,\s*'([^']*)'\s*(?:,\s*[^\)]*)?\)", re.IGNORECASE)
        self.re_find = re.compile(r"\bFIND\s*\(\s*([^,]+?)\s*,\s*'([^']*)'\s*\)", re.IGNORECASE)
        self.re_lod = re.compile(r"\{\s*(FIXED|INCLUDE|EXCLUDE)\b", re.IGNORECASE)
        self.re_median = re.compile(r"\bMEDIAN\s*\(\s*([^\)]+?)\s*\)", re.IGNORECASE)

    def remap(self, sql: str) -> Tuple[str, List[Flag]]:
        """
        Apply regex-based rewrites and collect flags for manual review.

        Returns:
            (remapped_sql, flags)
        """
        flags: List[Flag] = []
        if not sql:
            return sql, flags

        # Normalize comments style
        sql = self.re_comment_slashes.sub('--', sql)

        # Replace booleans
        sql = self.re_true.sub('1', sql)
        sql = self.re_false.sub('0', sql)

        # Common function name rewrites
        sql = self.re_if.sub('IIF(', sql)
        sql = self.re_ifnull.sub('ISNULL(', sql)
        sql = self.re_now.sub('GETDATE()', sql)
        sql = self.re_today.sub('CAST(GETDATE() AS DATE)', sql)
        sql = self.re_length.sub('LEN(', sql)
        sql = self.re_substr.sub('SUBSTRING(', sql)
        sql = self.re_makedate.sub('DATEFROMPARTS(', sql)
        sql = self.re_makedatetime.sub('DATETIMEFROMPARTS(', sql)
        # LN() → LOG(), LOG() (Tableau, base-10) → LOG10()
        sql = self.re_ln.sub('LOG(', sql)
        sql = self.re_log.sub('LOG10(', sql)

        # Remove Tableau-style bracketed identifiers: [field] → field
        sql = self.re_bracket_ident.sub(r"\1", sql)

        # Type-like functions
        sql = self.re_int.sub(r"CAST(\1 AS INT)", sql)
        sql = self.re_str.sub(rf"CAST(\1 AS VARCHAR({self.varchar_default_len}))", sql)
        sql = self.re_float.sub(r"CAST(\1 AS FLOAT)", sql)
        sql = self.re_date_cast.sub(r"CAST(\1 AS DATE)", sql)

        # SPLIT: first token only (index = 1). Others flagged.
        def _split_rewrite(m: re.Match) -> str:
            s = m.group(1).strip()
            delim = m.group(2)
            idx = m.group(3).strip()
            if idx == '1':
                return f"SUBSTRING({s}, 1, CHARINDEX('{delim}', {s}) - 1)"
            self._flag_lines(sql, rf"\bSPLIT\s*\(\s*{re.escape(s)}\s*,\s*'{re.escape(delim)}'\s*,\s*{idx}\s*\)",
                             "SPLIT with index != 1 requires manual rewrite", flags)
            return m.group(0)
        sql = self.re_split.sub(_split_rewrite, sql)

        # STARTSWITH/ENDSWITH/CONTAINS/FIND
        def _startswith(m: re.Match) -> str:
            s, prefix = m.group(1).strip(), m.group(2)
            return f"CHARINDEX('{prefix}', {s}) = 1"
        sql = self.re_startswith.sub(_startswith, sql)

        def _endswith(m: re.Match) -> str:
            s, suffix = m.group(1).strip(), m.group(2)
            return f"RIGHT({s}, LEN('{suffix}')) = '{suffix}'"
        sql = self.re_endswith.sub(_endswith, sql)

        def _contains(m: re.Match) -> str:
            s, needle = m.group(1).strip(), m.group(2)
            return f"CHARINDEX('{needle}', {s}) > 0"
        sql = self.re_contains.sub(_contains, sql)

        def _find(m: re.Match) -> str:
            s, needle = m.group(1).strip(), m.group(2)
            return f"CHARINDEX('{needle}', {s})"
        sql = self.re_find.sub(_find, sql)

        # MEDIAN → flag for manual rewrite (PERCENTILE_CONT WITHIN GROUP)
        if self.re_median.search(sql):
            self._flag_lines(sql, r"\bMEDIAN\s*\(", "MEDIAN requires PERCENTILE_CONT(0.5) WITHIN GROUP rewrite", flags)

        # LOD expressions → flag
        if self.re_lod.search(sql):
            self._flag_lines(sql, r"\{\s*(FIXED|INCLUDE|EXCLUDE)\b", "Tableau LOD expressions are not supported", flags)

        return sql, flags

    def _flag_lines(self, sql: str, pattern: str, reason: str, flags: List[Flag]) -> None:
        """Add a flag for each line matching the given pattern (case-insensitive)."""
        try:
            rx = re.compile(pattern, re.IGNORECASE)
        except re.error:
            return
        for i, line in enumerate(sql.split('\n'), start=1):
            if rx.search(line):
                flags.append((i, reason))


def apply_regex_remapping(sql: str, varchar_default_len: int = 20) -> Tuple[str, List[Flag]]:
    """Convenience API for one-shot remapping and flag collection."""
    return RegexRemapper(varchar_default_len=varchar_default_len).remap(sql)


"""
Regex-based remapping helpers for Tableau → Microsoft Fabric (T-SQL) conversion.

This module centralizes conservative, order-aware regex transforms for common
Tableau patterns. It is designed to be used as a preprocessing step before or
after token-based conversion.

Notes:
- Transforms are conservative and try to avoid breaking valid SQL. When an
  automatic rewrite is ambiguous, the function returns the input unchanged and
  records a flag for manual review.
- For bracketed identifiers (e.g. [field]) we normalize to bare identifiers to
  make subsequent regex and token rules easier to match consistently.
"""

import re
from typing import List, Tuple, Optional, Dict


Flag = Tuple[int, str]  # (line_number, reason)


class RegexRemapper:
    def __init__(self, varchar_default_len: int = 20) -> None:
        self.varchar_default_len = varchar_default_len

        # Precompiled patterns used across remaps
        self.re_bracket_ident = re.compile(r"\[([^\]]+)\]")
        self.re_if = re.compile(r"\bIF\s*\(", re.IGNORECASE)
        self.re_ifnull = re.compile(r"\bIFNULL\s*\(", re.IGNORECASE)
        self.re_true = re.compile(r"\bTRUE\b", re.IGNORECASE)
        self.re_false = re.compile(r"\bFALSE\b", re.IGNORECASE)
        self.re_comment_slashes = re.compile(r"//")
        self.re_now = re.compile(r"\bNOW\s*\(\s*\)", re.IGNORECASE)
        self.re_today = re.compile(r"\bTODAY\s*\(\s*\)", re.IGNORECASE)
        self.re_length = re.compile(r"\bLENGTH\s*\(", re.IGNORECASE)
        self.re_substr = re.compile(r"\bSUBSTR\s*\(", re.IGNORECASE)
        self.re_makedate = re.compile(r"\bMAKEDATE\s*\(", re.IGNORECASE)
        self.re_makedatetime = re.compile(r"\bMAKEDATETIME\s*\(", re.IGNORECASE)
        self.re_ln = re.compile(r"\bLN\s*\(", re.IGNORECASE)
        self.re_log = re.compile(r"\bLOG\s*\(", re.IGNORECASE)
        self.re_int = re.compile(r"\bINT\s*\(\s*([^\)]+?)\s*\)", re.IGNORECASE)
        self.re_str = re.compile(r"\bSTR\s*\(\s*([^\)]+?)\s*\)", re.IGNORECASE)
        self.re_float = re.compile(r"\bFLOAT\s*\(\s*([^\)]+?)\s*\)", re.IGNORECASE)
        self.re_date_cast = re.compile(r"\bDATE\s*\(\s*([^\)]+?)\s*\)", re.IGNORECASE)
        self.re_split = re.compile(r"\bSPLIT\s*\(\s*([^,]+?)\s*,\s*'([^']*)'\s*,\s*(\d+)\s*\)", re.IGNORECASE)
        self.re_startswith = re.compile(r"\bSTARTSWITH\s*\(\s*([^,]+?)\s*,\s*'([^']*)'\s*\)", re.IGNORECASE)
        self.re_endswith = re.compile(r"\bENDSWITH\s*\(\s*([^,]+?)\s*,\s*'([^']*)'\s*\)", re.IGNORECASE)
        self.re_contains = re.compile(r"\bCONTAINS\s*\(\s*([^,]+?)\s*,\s*'([^']*)'\s*(?:,\s*[^\)]*)?\)", re.IGNORECASE)
        self.re_find = re.compile(r"\bFIND\s*\(\s*([^,]+?)\s*,\s*'([^']*)'\s*\)", re.IGNORECASE)
        self.re_lod = re.compile(r"\{\s*(FIXED|INCLUDE|EXCLUDE)\b", re.IGNORECASE)
        self.re_median = re.compile(r"\bMEDIAN\s*\(\s*([^\)]+?)\s*\)", re.IGNORECASE)

    def remap(self, sql: str) -> Tuple[str, List[Flag]]:
        """
        Apply regex-based rewrites and collect flags for manual review.

        Returns:
            (remapped_sql, flags)
        """
        flags: List[Flag] = []
        if not sql:
            return sql, flags

        # Normalize comments style
        sql = self.re_comment_slashes.sub('--', sql)

        # Replace booleans
        sql = self.re_true.sub('1', sql)
        sql = self.re_false.sub('0', sql)

        # Common function name rewrites
        sql = self.re_if.sub('IIF(', sql)
        sql = self.re_ifnull.sub('ISNULL(', sql)
        sql = self.re_now.sub('GETDATE()', sql)
        sql = self.re_today.sub('CAST(GETDATE() AS DATE)', sql)
        sql = self.re_length.sub('LEN(', sql)
        sql = self.re_substr.sub('SUBSTRING(', sql)
        sql = self.re_makedate.sub('DATEFROMPARTS(', sql)
        sql = self.re_makedatetime.sub('DATETIMEFROMPARTS(', sql)
        # LN() → LOG(), LOG() (Tableau, base-10) → LOG10()
        sql = self.re_ln.sub('LOG(', sql)
        sql = self.re_log.sub('LOG10(', sql)

        # Remove Tableau-style bracketed identifiers: [field] → field
        sql = self.re_bracket_ident.sub(r"\1", sql)

        # Type-like functions
        sql = self.re_int.sub(r"CAST(\1 AS INT)", sql)
        sql = self.re_str.sub(rf"CAST(\1 AS VARCHAR({self.varchar_default_len}))", sql)
        sql = self.re_float.sub(r"CAST(\1 AS FLOAT)", sql)
        sql = self.re_date_cast.sub(r"CAST(\1 AS DATE)", sql)

        # SPLIT: first token only (index = 1). Others flagged.
        def _split_rewrite(m: re.Match) -> str:
            s = m.group(1).strip()
            delim = m.group(2)
            idx = m.group(3).strip()
            if idx == '1':
                return f"SUBSTRING({s}, 1, CHARINDEX('{delim}', {s}) - 1)"
            self._flag_lines(sql, rf"\bSPLIT\s*\(\s*{re.escape(s)}\s*,\s*'{re.escape(delim)}'\s*,\s*{idx}\s*\)",
                             "SPLIT with index != 1 requires manual rewrite", flags)
            return m.group(0)
        sql = self.re_split.sub(_split_rewrite, sql)

        # STARTSWITH/ENDSWITH/CONTAINS/FIND
        def _startswith(m: re.Match) -> str:
            s, prefix = m.group(1).strip(), m.group(2)
            return f"CHARINDEX('{prefix}', {s}) = 1"
        sql = self.re_startswith.sub(_startswith, sql)

        def _endswith(m: re.Match) -> str:
            s, suffix = m.group(1).strip(), m.group(2)
            return f"RIGHT({s}, LEN('{suffix}')) = '{suffix}'"
        sql = self.re_endswith.sub(_endswith, sql)

        def _contains(m: re.Match) -> str:
            s, needle = m.group(1).strip(), m.group(2)
            return f"CHARINDEX('{needle}', {s}) > 0"
        sql = self.re_contains.sub(_contains, sql)

        def _find(m: re.Match) -> str:
            s, needle = m.group(1).strip(), m.group(2)
            return f"CHARINDEX('{needle}', {s})"
        sql = self.re_find.sub(_find, sql)

        # MEDIAN → flag for manual rewrite (PERCENTILE_CONT WITHIN GROUP)
        if self.re_median.search(sql):
            self._flag_lines(sql, r"\bMEDIAN\s*\(", "MEDIAN requires PERCENTILE_CONT(0.5) WITHIN GROUP rewrite", flags)

        # LOD expressions → flag
        if self.re_lod.search(sql):
            self._flag_lines(sql, r"\{\s*(FIXED|INCLUDE|EXCLUDE)\b", "Tableau LOD expressions are not supported", flags)

        return sql, flags

    def _flag_lines(self, sql: str, pattern: str, reason: str, flags: List[Flag]) -> None:
        """Add a flag for each line matching the given pattern (case-insensitive)."""
        try:
            rx = re.compile(pattern, re.IGNORECASE)
        except re.error:
            return
        for i, line in enumerate(sql.split('\n'), start=1):
            if rx.search(line):
                flags.append((i, reason))


def apply_regex_remapping(sql: str, varchar_default_len: int = 20) -> Tuple[str, List[Flag]]:
    """Convenience API for one-shot remapping and flag collection."""
    return RegexRemapper(varchar_default_len=varchar_default_len).remap(sql)


