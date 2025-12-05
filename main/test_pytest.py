import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from components.data_cleaner import SQLCleaner
from components.sql_parser import SQLConverter
from components.Regex_remapping import apply_regex_remapping

class TestSQLCleaner:
    def test_extra_whitespace(self):
        cleaner = SQLCleaner()

        # Test Input
        test = "SELECT * FROM table WHERE        id = 1          "
        output = cleaner.clean_query(test)

        assert "  " not in output
        assert output == "SELECT * FROM table WHERE id = 1"

    def test_remove_extra_lines(self):
        cleaner = SQLCleaner()

        # Test Input
        test = "SELECT * FROM table WHERE id = 1 \n\n"
        output = cleaner.clean_query(test)

        assert "\n" not in output
        assert output == "SELECT * FROM table WHERE id = 1"


class TestCommentExtraction:
    def test_extract_comments(self):
        cleaner = SQLCleaner()

        # Test Input
        test = "SELECT * FROM table WHERE id = 1 -- comment HELLO WORLD"
        output, comments = cleaner.extract_comments(test)

        assert comments[0] == "-- comment HELLO WORLD"
        assert output == "SELECT * FROM table WHERE id = 1"



if __name__ == "__main__":
    pytest.main()


