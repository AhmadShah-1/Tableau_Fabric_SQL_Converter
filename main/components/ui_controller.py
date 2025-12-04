"""
UI Controller Module

This module provides the Tkinter-based graphical user interface for the SQL converter.
It implements the application workflow following the design flowchart:

AI was utilized for the tkinter GUI design and layout.

This file is responsible for:
- UI components and layout
- Event handling (callbacks from main.ipynb)
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext

class SQLConverterUI:
    def __init__(self, root, callbacks=None):
        self.root = root
        self.root.title("Tableau to Fabric SQL Converter")
        self.root.geometry("1200x800")
        
        # Store callbacks (callbacks from main.ipynb)
        self.callbacks = callbacks or {}
        
        # State variables
        self.current_file_path = None
        self.tableau_sql = ""
        self.fabric_sql = ""
        self.current_metrics = None
        self.flagged_items = []
        
        # Setup UI
        self._setup_ui()
        
    def _setup_ui(self):
        """Setup the main UI components and layout."""
        # Configure root window
        self.root.configure(bg='#f0f0f0')
        
        main_container = ttk.Frame(self.root, padding="10")
        main_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_container.columnconfigure(0, weight=1)
        main_container.rowconfigure(2, weight=1)
        
        self._create_header_section(main_container)
        self._create_file_section(main_container)
        self._create_preview_section(main_container)
        self._create_action_section(main_container)
        self._create_status_section(main_container)
    
    def _create_header_section(self, parent):
        """Create the header section with title and description."""
        header_frame = ttk.Frame(parent)
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        title_label = ttk.Label(
            header_frame, 
            text="Tableau to Fabric SQL Converter",
            font=('Arial', 18, 'bold')
        )
        title_label.grid(row=0, column=0, sticky=tk.W)
        
        desc_label = ttk.Label(
            header_frame,
            text="Convert Tableau SQL queries to Microsoft Fabric SQL syntax",
            font=('Arial', 10)
        )
        desc_label.grid(row=1, column=0, sticky=tk.W)
    
    def _create_file_section(self, parent):
        """Create the file selection and info section."""
        file_frame = ttk.LabelFrame(parent, text="File Selection", padding="10")
        file_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        file_frame.columnconfigure(1, weight=1)
        
        ttk.Label(file_frame, text="SQL File:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        
        self.file_path_var = tk.StringVar()
        file_entry = ttk.Entry(file_frame, textvariable=self.file_path_var, state='readonly')
        file_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 5))
        
        browse_btn = ttk.Button(file_frame, text="Browse...", command=self._on_browse)
        browse_btn.grid(row=0, column=2, padx=(0, 5))
        
        self.load_btn = ttk.Button(file_frame, text="Load & Convert", command=self._on_load_convert)
        self.load_btn.grid(row=0, column=3)
        
        self.file_info_var = tk.StringVar(value="No file loaded")
        info_label = ttk.Label(file_frame, textvariable=self.file_info_var, font=('Arial', 9, 'italic'))
        info_label.grid(row=1, column=0, columnspan=4, sticky=tk.W, pady=(5, 0))
    
    def _create_preview_section(self, parent):
        """Create the split-pane SQL preview section."""
        preview_frame = ttk.LabelFrame(parent, text="SQL Preview", padding="10")
        preview_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        preview_frame.columnconfigure(0, weight=1)
        preview_frame.columnconfigure(1, weight=1)
        preview_frame.rowconfigure(1, weight=1)

        tableau_label = ttk.Label(preview_frame, text="Tableau SQL (Original)", font=('Arial', 10, 'bold'))
        tableau_label.grid(row=0, column=0, sticky=tk.W, padx=(0, 5), pady=(0, 5))
        fabric_label = ttk.Label(preview_frame, text="Fabric SQL (Converted)", font=('Arial', 10, 'bold'))
        fabric_label.grid(row=0, column=1, sticky=tk.W, pady=(0, 5))

        left_container = ttk.Frame(preview_frame)
        left_container.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        right_container = ttk.Frame(preview_frame)
        right_container.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        preview_frame.rowconfigure(1, weight=1)
        for c in (left_container, right_container):
            c.columnconfigure(1, weight=1)
            c.rowconfigure(0, weight=1)

        self.left_gutter = tk.Text(left_container, width=5, padx=4, takefocus=0, borderwidth=0,
                                   background='#f4f4f4', state='disabled', font=('Courier New', 9))
        self.left_gutter.grid(row=0, column=0, sticky=(tk.N, tk.S))
        self.right_gutter = tk.Text(right_container, width=5, padx=4, takefocus=0, borderwidth=0,
                                    background='#f4f4f4', state='disabled', font=('Courier New', 9))
        self.right_gutter.grid(row=0, column=0, sticky=(tk.N, tk.S))

        self.tableau_text = tk.Text(left_container, wrap='none', undo=True, font=('Courier New', 9))
        self.tableau_text.grid(row=0, column=1, sticky=(tk.N, tk.S, tk.E, tk.W))
        self.fabric_text = tk.Text(right_container, wrap='none', undo=True, font=('Courier New', 9))
        self.fabric_text.grid(row=0, column=1, sticky=(tk.N, tk.S, tk.E, tk.W))

        self.left_scroll = ttk.Scrollbar(left_container, orient='vertical')
        self.left_scroll.grid(row=0, column=2, sticky=(tk.N, tk.S))
        self.right_scroll = ttk.Scrollbar(right_container, orient='vertical')
        self.right_scroll.grid(row=0, column=2, sticky=(tk.N, tk.S))

        self.left_hscroll = ttk.Scrollbar(left_container, orient='horizontal')
        self.left_hscroll.grid(row=1, column=1, sticky=(tk.E, tk.W))
        self.right_hscroll = ttk.Scrollbar(right_container, orient='horizontal')
        self.right_hscroll.grid(row=1, column=1, sticky=(tk.E, tk.W))

        self.tableau_text.configure(yscrollcommand=self._sync_scroll_from_left, xscrollcommand=self.left_hscroll.set)
        self.fabric_text.configure(yscrollcommand=self._sync_scroll_from_right, xscrollcommand=self.right_hscroll.set)
        self.left_scroll.configure(command=self._scroll_both_y)
        self.right_scroll.configure(command=self._scroll_both_y)
        self.left_hscroll.configure(command=self.tableau_text.xview)
        self.right_hscroll.configure(command=self.fabric_text.xview)

        for widget in (self.tableau_text, self.fabric_text):
            widget.bind('<MouseWheel>', self._on_mousewheel_sync)
            widget.bind('<KeyPress>', self._update_gutters_debounced)
            widget.bind('<ButtonRelease-1>', self._update_gutters_debounced)

        self.tableau_text.tag_configure('error', foreground='red')
    
    def _create_action_section(self, parent):
        """Create the action buttons section."""
        action_frame = ttk.Frame(parent)
        action_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Save button
        self.save_btn = ttk.Button(
            action_frame,
            text="💾 Save Converted SQL",
            command=self._on_save,
            state='disabled'
        )
        self.save_btn.grid(row=0, column=0, padx=(0, 10))
        
        clear_btn = ttk.Button(action_frame, text="🗑 Clear", command=self._on_clear)
        clear_btn.grid(row=0, column=2, padx=(0, 10))
        
        help_btn = ttk.Button(action_frame, text="❓ Help", command=self._show_help)
        help_btn.grid(row=0, column=3)
    
    def _create_status_section(self, parent):
        """Create the status bar and flagged items section."""
        status_frame = ttk.LabelFrame(parent, text="Status & Flagged Items", padding="10")
        status_frame.grid(row=4, column=0, sticky=(tk.W, tk.E))
        status_frame.columnconfigure(0, weight=1)
        
        self.status_var = tk.StringVar(value="Ready. Please load a SQL file to begin.")
        status_label = ttk.Label(status_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_label.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        
        self.flagged_text = scrolledtext.ScrolledText(
            status_frame,
            wrap=tk.WORD,
            height=4,
            font=('Courier New', 8)
        )
        self.flagged_text.grid(row=1, column=0, sticky=(tk.W, tk.E))
        self.flagged_text.insert('1.0', "Flagged items will appear here...")
        self.flagged_text.configure(state='disabled')
    
    # Event Handlers 
    
    def _on_browse(self):
        if 'on_browse' in self.callbacks:
            self.callbacks['on_browse']()
            
    def _on_load_convert(self):
        if 'on_convert' in self.callbacks:
            self.callbacks['on_convert']()
            
    def _on_save(self):
        if 'on_save' in self.callbacks:
            self.callbacks['on_save']()
            
    def _on_clear(self):
        if 'on_clear' in self.callbacks:
            self.callbacks['on_clear']()

    # Public UI Methods 
    
    def set_file_path(self, path):
        self.current_file_path = path
        self.file_path_var.set(path)
        
    def set_file_info(self, info_text):
        self.file_info_var.set(info_text)
        
    def set_status(self, text):
        self.status_var.set(text)
        self.root.update()

    def set_tableau_sql(self, sql_text):
        self.tableau_sql = sql_text
        self.tableau_text.configure(state='normal')
        self.tableau_text.delete('1.0', tk.END)
        self.tableau_text.insert('1.0', sql_text)
        self.tableau_text.configure(state='disabled')
        self._refresh_line_numbers()

    def set_fabric_sql(self, sql_text):
        self.fabric_sql = sql_text
        self.fabric_text.configure(state='normal')
        self.fabric_text.delete('1.0', tk.END)
        self.fabric_text.insert('1.0', sql_text)
        # leave editable so users can change before saving
        self._refresh_line_numbers()
        
    def get_fabric_sql(self):
        return self.fabric_text.get('1.0', tk.END).rstrip()

    def enable_save_button(self):
        self.save_btn.configure(state='normal')
        
    def disable_save_button(self):
        self.save_btn.configure(state='disabled')

    def display_flagged_items(self, flagged_items, metrics=None):
        self.flagged_items = flagged_items
        self.current_metrics = metrics
        
        self.flagged_text.configure(state='normal')
        self.flagged_text.delete('1.0', tk.END)
        
        if not flagged_items:
            self.flagged_text.insert('1.0', "✓ No flagged items - all conversions successful!")
        else:
            header = f"⚠ {len(flagged_items)} ITEM(S) REQUIRE MANUAL REVIEW:\n" + "="*70 + "\n\n"
            self.flagged_text.insert('1.0', header)
            
            for line_num, reason in flagged_items:
                item_text = f"Line {line_num}: {reason}\n"
                self.flagged_text.insert(tk.END, item_text)
                # Highlight those lines in the Tableau pane (red)
                try:
                    if line_num and isinstance(line_num, int) and line_num > 0:
                        start = f"{line_num}.0"
                        end = f"{line_num}.end"
                        self.tableau_text.configure(state='normal')
                        self.tableau_text.tag_remove('error', start, end)
                        self.tableau_text.tag_add('error', start, end)
                        self.tableau_text.configure(state='disabled')
                except Exception:
                    pass
            
            # Add unsupported functions if any
            if metrics:
                metrics_dict = metrics.to_dict()
                unsupported = metrics_dict.get('unsupported_functions', [])
                if unsupported:
                    self.flagged_text.insert(tk.END, f"\n\nUnsupported Functions: {', '.join(unsupported)}\n")
        
        self.flagged_text.configure(state='disabled')
        self._highlight_from_metrics()
        self._refresh_line_numbers()

    def clear_all(self):
        # Clear text areas
        self.tableau_text.configure(state='normal')
        self.tableau_text.delete('1.0', tk.END)
        self.tableau_text.configure(state='disabled')
        
        self.fabric_text.configure(state='normal')
        self.fabric_text.delete('1.0', tk.END)
        self.fabric_text.configure(state='disabled')
        
        self.flagged_text.configure(state='normal')
        self.flagged_text.delete('1.0', tk.END)
        self.flagged_text.insert('1.0', "Flagged items will appear here...")
        self.flagged_text.configure(state='disabled')
        
        # Reset variables
        self.current_file_path = None
        self.file_path_var.set("")
        self.file_info_var.set("No file loaded")
        self.tableau_sql = ""
        self.fabric_sql = ""
        self.current_metrics = None
        self.flagged_items = []
        
        self.disable_save_button()
        self.status_var.set("Ready. Please load a SQL file to begin.")

    def show_info(self, title, message):
        messagebox.showinfo(title, message)
        
    def show_warning(self, title, message):
        messagebox.showwarning(title, message)
        
    def show_error(self, title, message):
        messagebox.showerror(title, message)

    def _highlight_from_metrics(self):
        """Highlight lines containing unsupported or special-case functions."""
        try:
            if not self.current_metrics or not self.tableau_sql:
                return
            # Build set of line numbers to highlight
            lines_to_mark = set()
            content_lines = self.tableau_sql.split('\n')
            # Unsupported functions
            metrics = self.current_metrics.to_dict()
            for func in metrics.get('unsupported_functions', []):
                try:
                    import re
                    pattern = re.compile(r"\\b" + re.escape(func) + r"\\s*\\(", re.IGNORECASE)
                except Exception:
                    pattern = None
                if pattern:
                    for idx, line in enumerate(content_lines, start=1):
                        if pattern.search(line):
                            lines_to_mark.add(idx)
            # Special patterns that require manual rewrite
            special_patterns = [r'\\bSTARTSWITH\\s*\\(', r'\\bENDSWITH\\s*\\(', r'\\bCONTAINS\\s*\\(']
            special_patterns.append(r'\{\s*(FIXED|INCLUDE|EXCLUDE)\b')
            import re
            specials = [re.compile(pat, re.IGNORECASE) for pat in special_patterns]
            for idx, line in enumerate(content_lines, start=1):
                if any(p.search(line) for p in specials):
                    lines_to_mark.add(idx)

            # Apply tags in the Tableau view
            if lines_to_mark:
                self.tableau_text.configure(state='normal')
                for ln in lines_to_mark:
                    try:
                        self.tableau_text.tag_add('error', f"{ln}.0", f"{ln}.end")
                    except Exception:
                        pass
                self.tableau_text.configure(state='disabled')
        except Exception:
            pass

    # Scrolling & Line Numbers
    def _scroll_both_y(self, *args):
        self.tableau_text.yview(*args)
        self.fabric_text.yview(*args)
        self.left_gutter.yview(*args)
        self.right_gutter.yview(*args)

    def _sync_scroll_from_left(self, first, last):
        self.left_scroll.set(first, last)
        self.right_scroll.set(first, last)
        self.fabric_text.yview_moveto(first)
        self.left_gutter.yview_moveto(first)
        self.right_gutter.yview_moveto(first)

    def _sync_scroll_from_right(self, first, last):
        self.right_scroll.set(first, last)
        self.left_scroll.set(first, last)
        self.tableau_text.yview_moveto(first)
        self.left_gutter.yview_moveto(first)
        self.right_gutter.yview_moveto(first)

    def _on_mousewheel_sync(self, event):
        delta = -1 * int(event.delta / 120)
        self.tableau_text.yview_scroll(delta, 'units')
        self.fabric_text.yview_scroll(delta, 'units')
        self.left_gutter.yview_scroll(delta, 'units')
        self.right_gutter.yview_scroll(delta, 'units')
        self._refresh_line_numbers()
        return 'break'

    def _refresh_line_numbers(self):
        for gutter, text in ((self.left_gutter, self.tableau_text), (self.right_gutter, self.fabric_text)):
            gutter.configure(state='normal')
            gutter.delete('1.0', tk.END)
            last_index = text.index('end-1c')
            total_lines = int(str(last_index).split('.')[0])
            lines = "\n".join(str(i) for i in range(1, total_lines + 1))
            gutter.insert('1.0', lines)
            gutter.configure(state='disabled')

    def _update_gutters_debounced(self, event=None):
        self.root.after(50, self._refresh_line_numbers)
    
    def _show_help(self):
        """Display help information."""
        help_text = """
TABLEAU TO FABRIC SQL CONVERTER - HELP

HOW TO USE:
1. Click 'Browse...' to select a Tableau SQL file (.sql or .txt)
2. Click 'Load & Convert' to convert the SQL
3. Review the converted SQL in the right pane
4. Check 'Flagged Items' section for any items needing manual review
5. Click 'Save Converted SQL' to save the result
6. You can edit the Fabric SQL pane directly before saving.

SUPPORTED CONVERSIONS:
• Date Functions (DATEADD, NOW, TODAY, MAKEDATE, etc.)
• String Functions (LENGTH, SUBSTR, CONTAINS, etc.)
• Aggregate Functions (SUM, AVG, COUNT, MEDIAN, etc.)
• Logical Functions (IF, IFNULL, etc.)
• Mathematical Functions (ROUND, SQRT, LN, LOG, etc.)
• Any other unsupported functions will be flagged for manual review (Program shall recieve incremental updates)

FLAGGED ITEMS:
If certain functions or syntax cannot be automatically converted,
they will be flagged for manual review. These items will appear
in the 'Flagged Items' section with explanations.

For more information, see the README.md file.
        """
        
        help_window = tk.Toplevel(self.root)
        help_window.title("Help - SQL Converter")
        help_window.geometry("600x500")
        
        help_text_widget = scrolledtext.ScrolledText(help_window, wrap=tk.WORD, font=('Arial', 10))
        help_text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        help_text_widget.insert('1.0', help_text)
        help_text_widget.configure(state='disabled')
        
        close_btn = ttk.Button(help_window, text="Close", command=help_window.destroy)
        close_btn.pack(pady=(0, 10))
    
    def run(self):
        """Start the UI main loop."""
        self.root.mainloop()
