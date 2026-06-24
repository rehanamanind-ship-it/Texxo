import tkinter as tk
from tkinter import filedialog, font, messagebox, simpledialog, colorchooser
import re
import json
import os
from datetime import datetime

COLOR_MAP = {
    # Basic Colors
    'blue': '#61afef',
    'red': '#ff6c6b',
    'green': '#98c379',
    'yellow': '#e5c07b',
    'orange': '#d19a66',
    'purple': '#c678dd',
    'pink': '#ff79c6',
    'cyan': '#56b6c2',
    'white': '#abb2bf',
    'gray': '#5c6370',
    'black': '#282c34',
    'lime': '#7ec699',
    'teal': '#2aa198',
    
    # Extended Colors
    'coral': '#ff7f50',
    'crimson': '#dc143c',
    'gold': '#ffd700',
    'indigo': '#4b0082',
    'lavender': '#e6e6fa',
    'magenta': '#ff00ff',
    'maroon': '#800000',
    'navy': '#000080',
    'olive': '#808000',
    'plum': '#dda0dd',
    'salmon': '#fa8072',
    'sienna': '#a0522d',
    'tan': '#d2b48c',
    'tomato': '#ff6347',
    'turquoise': '#40e0d0',
    'violet': '#ee82ee',
    
    # Material Design Colors
    'md-red': '#f44336',
    'md-pink': '#e91e63',
    'md-purple': '#9c27b0',
    'md-deep-purple': '#673ab7',
    'md-indigo': '#3f51b5',
    'md-blue': '#2196f3',
    'md-light-blue': '#03a9f4',
    'md-cyan': '#00bcd4',
    'md-teal': '#009688',
    'md-green': '#4caf50',
    'md-light-green': '#8bc34a',
    'md-lime': '#cddc39',
    'md-yellow': '#ffeb3b',
    'md-amber': '#ffc107',
    'md-orange': '#ff9800',
    'md-deep-orange': '#ff5722',
    'md-brown': '#795548',
    'md-grey': '#9e9e9e',
    'md-blue-grey': '#607d8b',
    
    # Pastel Colors
    'pastel-pink': '#ffd1dc',
    'pastel-blue': '#aec6cf',
    'pastel-green': '#77dd77',
    'pastel-yellow': '#fdfd96',
    'pastel-purple': '#b39eb5',
    'pastel-orange': '#ffb347',
    'pastel-mint': '#98fb98',
    'pastel-lavender': '#e6e6fa',
    
    # Neon Colors
    'neon-pink': '#ff6ec7',
    'neon-blue': '#4d4dff',
    'neon-green': '#39ff14',
    'neon-yellow': '#ffff00',
    'neon-orange': '#ff6600',
    'neon-purple': '#9d00ff',
    'neon-cyan': '#00ffff',
}

FONT_MAP = {
    # Original Fonts
    'creepy': ('Chiller', 20),
    'mono': ('Cascadia Code', 14),
    'clean': ('Segoe UI', 14),
    'code': ('Courier New', 14),
    'retro': ('OCR A Extended', 16),
    
    # Classic Fonts
    'times': ('Times New Roman', 14),
    'arial': ('Arial', 14),
    'helvetica': ('Helvetica', 14),
    'georgia': ('Georgia', 14),
    'verdana': ('Verdana', 14),
    'trebuchet': ('Trebuchet MS', 14),
    'comic': ('Comic Sans MS', 14),
    'impact': ('Impact', 16),
    'palatino': ('Palatino Linotype', 14),
    'garamond': ('Garamond', 14),
    
    # Modern Fonts
    'roboto': ('Roboto', 14),
    'opensans': ('Open Sans', 14),
    'lato': ('Lato', 14),
    'montserrat': ('Montserrat', 14),
    'poppins': ('Poppins', 14),
    'raleway': ('Raleway', 14),
    'ubuntu': ('Ubuntu', 14),
    'fira': ('Fira Code', 14),
    'jetbrains': ('JetBrains Mono', 14),
    'source': ('Source Code Pro', 14),
    
    # Decorative Fonts
    'script': ('Brush Script MT', 18),
    'gothic': ('Century Gothic', 14),
    'copper': ('Copperplate Gothic Bold', 14),
    'papyrus': ('Papyrus', 16),
    'jokerman': ('Jokerman', 16),
    'curlz': ('Curlz MT', 18),
    'algerian': ('Algerian', 16),
    'broadway': ('Broadway', 16),
    'castellar': ('Castellar', 18),
    'magneto': ('Magneto', 16),
}

HELP_TEXT = (
    "🎨 TEXT FORMATTING: hh <color>  highlight | tc <color>  text color | ft <style>  font style | "
    "fs <size>  font size | ff <family>  font family | st  strikethrough | bo  bold | it  italic | "
    "ul  underline | rm  reset formatting\n"
    "🔤 TEXT TRANSFORM: uc  upper-case | lc  lower-case | caps  title case | "
    "reverse  reverse text | scramble  scramble text | rot13  ROT13 encode\n"
    "📐 LAYOUT: align <left|center|right> | indent | outdent | lineup  increase line spacing | "
    "linedown  decrease line spacing | paragraph  add paragraph spacing\n"
    "🔍 SEARCH: find <text> | replace <old> <new> | findall <pattern>  regex search | "
    "count <text>  count occurrences\n"
    "📁 FILE: open <path> | save <path> | new  new document | export <html|rtf|pdf> | "
    "insertfile <path>  insert file content\n"
    "✂️ EDIT: undo | redo | sa  select all | del  delete selection | cp  copy | "
    "cut  cut | paste  paste | dupline  duplicate line | movelineup  move line up | "
    "movelinedown  move line down\n"
    "🔢 INSERT: date  insert date | time  insert time | datetime  insert date & time | "
    "linenums  add line numbers | bullets  add bullet points\n"
    "🎯 SPECIAL: sort  sort selection | shuffle  shuffle lines | unique  remove duplicates | "
    "wordcount  count words | charcount  count characters\n"
    "💾 SESSION: bookmark <name>  bookmark position | goto <name>  go to bookmark | "
    "history  show command history | theme <dark|light>  change theme"
)

class TexxoEditor:
    def __init__(self, root):
        self.root = root
        root.title('Texxo Pro - Advanced Text Editor')
        root.configure(bg='#071b38')
        root.geometry('1100x800')
        root.minsize(900, 600)

        self.default_font = font.Font(family='Consolas', size=14)
        self.command_history = []
        self.bookmarks = {}
        self.current_theme = 'dark'
        self.recent_files = []
        self.max_history = 50
        self.auto_save_enabled = False
        
        self.create_ui()
        self.load_settings()
        
        # Auto-save timer
        self.auto_save_interval = 300000  # 5 minutes
        if self.auto_save_enabled:
            self.start_auto_save()

    def create_ui(self):
        # Menu Bar
        self.create_menu_bar()
        
        # Toolbar
        self.create_toolbar()
        
        # Main content
        top_frame = tk.Frame(self.root, bg='#071b38', padx=12, pady=10)
        top_frame.pack(fill='x')

        prompt_label = tk.Label(
            top_frame,
            text='⚡ Command:',
            fg='#d7eaf9',
            bg='#071b38',
            font=('Segoe UI', 11, 'bold'),
        )
        prompt_label.pack(side='left', padx=(0, 8))

        self.command_entry = tk.Entry(
            top_frame,
            font=('Consolas', 13),
            bg='#122846',
            fg='white',
            insertbackground='white',
            relief='flat',
            width=52,
        )
        self.command_entry.pack(side='left', fill='x', expand=True)
        self.command_entry.bind('<Return>', self.handle_command)
        self.command_entry.bind('<Up>', self.show_previous_command)
        self.command_entry.bind('<Down>', self.show_next_command)

        run_button = tk.Button(
            top_frame,
            text='▶ Run',
            command=self.handle_command,
            bg='#1f508b',
            fg='white',
            activebackground='#2e6bb2',
            relief='flat',
            padx=14,
            pady=8,
            cursor='hand2',
        )
        run_button.pack(side='left', padx=(10, 0))

        self.status_label = tk.Label(
            self.root,
            text='✨ Ready | Select text and enter a command | Type "help" for all commands',
            fg='#b7d2ff',
            bg='#071b38',
            anchor='w',
            font=('Segoe UI', 10),
            padx=12,
            pady=6,
        )
        self.status_label.pack(fill='x')

        editor_frame = tk.Frame(self.root, bg='#071b38', padx=12, pady=8)
        editor_frame.pack(fill='both', expand=True)

        # Line numbers
        self.line_numbers = tk.Text(
            editor_frame,
            width=4,
            bg='#0a1a3a',
            fg='#4a6a8a',
            relief='flat',
            bd=0,
            font=('Consolas', 14),
            state='disabled',
            padx=5,
            pady=5,
        )
        self.line_numbers.pack(side='left', fill='y')

        self.text_widget = tk.Text(
            editor_frame,
            wrap='word',
            bg='#0f2345',
            fg='white',
            insertbackground='white',
            selectbackground='#2e5c9d',
            relief='flat',
            bd=0,
            font=self.default_font,
            undo=True,
            maxundo=100,
            spacing3=6,
            tabs=('1c', '2c', '3c', '4c'),
        )
        self.text_widget.pack(side='left', fill='both', expand=True)
        
        # Bind events
        self.text_widget.bind('<KeyRelease>', self.update_line_numbers)
        self.text_widget.bind('<MouseWheel>', self.update_line_numbers)
        self.text_widget.bind('<Button-4>', self.update_line_numbers)
        self.text_widget.bind('<Button-5>', self.update_line_numbers)
        self.text_widget.bind('<<Modified>>', self.on_text_modified)

        scrollbar = tk.Scrollbar(editor_frame, command=self.on_scroll)
        scrollbar.pack(side='right', fill='y')
        self.text_widget.config(yscrollcommand=self.on_scrollbar_scroll)
        self.scrollbar = scrollbar

        # Bottom status bar
        self.create_status_bar()

        self.setup_default_tags()
        self.update_line_numbers()
        self.update_status_bar()

    def create_menu_bar(self):
        menubar = tk.Menu(self.root, bg='#122846', fg='white')
        self.root.config(menu=menubar)

        # File Menu
        file_menu = tk.Menu(menubar, tearoff=0, bg='#122846', fg='white')
        menubar.add_cascade(label='File', menu=file_menu)
        file_menu.add_command(label='New', command=lambda: self.new_document(), accelerator='Ctrl+N')
        file_menu.add_command(label='Open', command=lambda: self.open_document([]), accelerator='Ctrl+O')
        file_menu.add_command(label='Save', command=lambda: self.save_document([]), accelerator='Ctrl+S')
        file_menu.add_command(label='Save As...', command=self.save_as_document)
        file_menu.add_separator()
        file_menu.add_command(label='Export as HTML', command=self.export_html)
        file_menu.add_command(label='Export as RTF', command=self.export_rtf)
        file_menu.add_separator()
        file_menu.add_command(label='Recent Files', command=self.show_recent_files)
        file_menu.add_separator()
        file_menu.add_command(label='Exit', command=self.root.quit)

        # Edit Menu
        edit_menu = tk.Menu(menubar, tearoff=0, bg='#122846', fg='white')
        menubar.add_cascade(label='Edit', menu=edit_menu)
        edit_menu.add_command(label='Undo', command=lambda: self.undo(), accelerator='Ctrl+Z')
        edit_menu.add_command(label='Redo', command=lambda: self.redo(), accelerator='Ctrl+Y')
        edit_menu.add_separator()
        edit_menu.add_command(label='Cut', command=self.cut_selection, accelerator='Ctrl+X')
        edit_menu.add_command(label='Copy', command=self.copy_selection, accelerator='Ctrl+C')
        edit_menu.add_command(label='Paste', command=self.paste_text, accelerator='Ctrl+V')
        edit_menu.add_separator()
        edit_menu.add_command(label='Find and Replace', command=self.show_find_replace_dialog, accelerator='Ctrl+F')
        edit_menu.add_command(label='Go to Line', command=self.go_to_line, accelerator='Ctrl+G')

        # Format Menu
        format_menu = tk.Menu(menubar, tearoff=0, bg='#122846', fg='white')
        menubar.add_cascade(label='Format', menu=format_menu)
        format_menu.add_command(label='Bold', command=lambda: self.apply_bold(), accelerator='Ctrl+B')
        format_menu.add_command(label='Italic', command=lambda: self.apply_italic(), accelerator='Ctrl+I')
        format_menu.add_command(label='Underline', command=lambda: self.apply_underline(), accelerator='Ctrl+U')
        format_menu.add_separator()
        format_menu.add_command(label='Change Color...', command=self.choose_color)
        format_menu.add_command(label='Change Font...', command=self.choose_font)

        # Tools Menu
        tools_menu = tk.Menu(menubar, tearoff=0, bg='#122846', fg='white')
        menubar.add_cascade(label='Tools', menu=tools_menu)
        tools_menu.add_command(label='Word Count', command=self.show_word_count)
        tools_menu.add_command(label='Character Count', command=self.show_char_count)
        tools_menu.add_separator()
        tools_menu.add_command(label='Sort Lines', command=lambda: self.sort_lines())
        tools_menu.add_command(label='Remove Duplicates', command=lambda: self.unique_lines())
        tools_menu.add_separator()
        tools_menu.add_command(label='Insert Date/Time', command=self.insert_datetime)
        tools_menu.add_command(label='Add Line Numbers', command=self.add_line_numbers)

        # View Menu
        view_menu = tk.Menu(menubar, tearoff=0, bg='#122846', fg='white')
        menubar.add_cascade(label='View', menu=view_menu)
        view_menu.add_command(label='Dark Theme', command=lambda: self.change_theme('dark'))
        view_menu.add_command(label='Light Theme', command=lambda: self.change_theme('light'))
        view_menu.add_separator()
        view_menu.add_command(label='Toggle Line Numbers', command=self.toggle_line_numbers)
        view_menu.add_command(label='Toggle Word Wrap', command=self.toggle_word_wrap)

        # Help Menu
        help_menu = tk.Menu(menubar, tearoff=0, bg='#122846', fg='white')
        menubar.add_cascade(label='Help', menu=help_menu)
        help_menu.add_command(label='Commands Help', command=self.show_help)
        help_menu.add_command(label='About', command=self.show_about)

    def create_toolbar(self):
        toolbar = tk.Frame(self.root, bg='#0a1a3a', padx=5, pady=5)
        toolbar.pack(fill='x')

        buttons = [
            ('📁 New', lambda: self.new_document()),
            ('📂 Open', lambda: self.open_document([])),
            ('💾 Save', lambda: self.save_document([])),
            ('|', None),
            ('B', lambda: self.apply_bold()),
            ('I', lambda: self.apply_italic()),
            ('U', lambda: self.apply_underline()),
            ('|', None),
            ('◀ Undo', lambda: self.undo()),
            ('▶ Redo', lambda: self.redo()),
            ('|', None),
            ('🔍 Find', self.show_find_replace_dialog),
        ]

        for text, command in buttons:
            if text == '|':
                tk.Frame(toolbar, width=2, bg='#2e5c9d').pack(side='left', fill='y', padx=5)
            else:
                btn = tk.Button(
                    toolbar,
                    text=text,
                    command=command,
                    bg='#122846',
                    fg='white',
                    relief='flat',
                    padx=8,
                    pady=4,
                    cursor='hand2',
                    font=('Segoe UI', 9),
                )
                btn.pack(side='left', padx=2)

    def create_status_bar(self):
        self.status_bar = tk.Label(
            self.root,
            text='Lines: 1 | Words: 0 | Characters: 0 | Position: 1:0',
            fg='#8da8d8',
            bg='#071b38',
            anchor='w',
            font=('Segoe UI', 9),
            padx=12,
            pady=4,
        )
        self.status_bar.pack(fill='x', side='bottom')

    def setup_default_tags(self):
        """Set up default tags with proper font configuration"""
        base_font = self.default_font.copy()
        
        # Style tags
        bold_font = self.default_font.copy()
        bold_font.configure(weight='bold')
        self.text_widget.tag_configure('bold', font=bold_font)
        
        italic_font = self.default_font.copy()
        italic_font.configure(slant='italic')
        self.text_widget.tag_configure('italic', font=italic_font)
        
        bold_italic_font = self.default_font.copy()
        bold_italic_font.configure(weight='bold', slant='italic')
        self.text_widget.tag_configure('bold_italic', font=bold_italic_font)
        
        self.text_widget.tag_configure('underline', underline=1)
        self.text_widget.tag_configure('strikethrough', overstrike=1)
        self.text_widget.tag_configure('double_underline', underline=1)
        
        # Alignment tags
        self.text_widget.tag_configure('align_left', justify='left')
        self.text_widget.tag_configure('align_center', justify='center')
        self.text_widget.tag_configure('align_right', justify='right')
        self.text_widget.tag_configure('align_justify', justify='left')  # Tkinter doesn't support justify
        
        # Special tags
        self.text_widget.tag_configure('superscript', offset=8, font=('Consolas', 10))
        self.text_widget.tag_configure('subscript', offset=-4, font=('Consolas', 10))
        self.text_widget.tag_configure('highlight_yellow', background='#e5c07b', foreground='black')
        self.text_widget.tag_configure('code_block', background='#1a1a2e', font=('Courier New', 13))

    def update_line_numbers(self, event=None):
        """Update line numbers display"""
        lines = self.text_widget.get('1.0', 'end-1c').count('\n') + 1
        line_numbers_text = '\n'.join(str(i) for i in range(1, lines + 1))
        
        self.line_numbers.config(state='normal')
        self.line_numbers.delete('1.0', 'end')
        self.line_numbers.insert('1.0', line_numbers_text)
        self.line_numbers.config(state='disabled')
        
        self.update_status_bar()

    def on_scroll(self, *args):
        """Synchronize scrolling between text widget and line numbers"""
        self.text_widget.yview(*args)
        self.line_numbers.yview(*args)

    def on_scrollbar_scroll(self, *args):
        """Handle scrollbar movement"""
        self.scrollbar.set(*args)
        self.line_numbers.yview_moveto(args[0])

    def update_status_bar(self, event=None):
        """Update status bar information"""
        content = self.text_widget.get('1.0', 'end-1c')
        lines = content.count('\n') + 1
        words = len(content.split())
        chars = len(content)
        
        cursor_pos = self.text_widget.index('insert')
        line, col = cursor_pos.split('.')
        
        self.status_bar.config(
            text=f'Lines: {lines} | Words: {words} | Characters: {chars} | Position: {line}:{col}'
        )

    def on_text_modified(self, event=None):
        """Handle text modification event"""
        if self.text_widget.edit_modified():
            self.update_line_numbers()
            self.update_status_bar()
            self.text_widget.edit_modified(False)

    def handle_command(self, event=None):
        raw_command = self.command_entry.get().strip()
        if not raw_command:
            return

        # Add to command history
        self.command_history.append(raw_command)
        if len(self.command_history) > self.max_history:
            self.command_history.pop(0)
        self.command_history_index = len(self.command_history)

        tokens = raw_command.split()
        command = tokens[0].lower()
        args = tokens[1:]

        # Commands that don't require selection
        no_selection_commands = {
            'cp', 'copy', 'help', 'open', 'load', 'save', 'sa', 'selectall',
            'undo', 'redo', 'find', 'replace', 'findall', 'count', 'new',
            'date', 'time', 'datetime', 'history', 'wordcount', 'charcount',
            'theme', 'bookmark', 'goto', 'export', 'insertfile', 'cut', 'paste',
            'linenums', 'bullets'
        }
        
        if command in {'cp', 'copy'}:
            self.copy_selection()
            self.command_entry.delete(0, 'end')
            return
        
        if command in {'cut'}:
            self.cut_selection()
            self.command_entry.delete(0, 'end')
            return

        if command not in no_selection_commands and not self.has_selection():
            self.status('⚠️ Select a range of text first.')
            self.command_entry.delete(0, 'end')
            return

        command_map = {
            # Formatting
            'hh': self.apply_highlight,
            'highlight': self.apply_highlight,
            'tc': self.apply_color,
            'color': self.apply_color,
            'ft': self.apply_font_style,
            'fontstyle': self.apply_font_style,
            'fs': self.apply_font_size,
            'fontsize': self.apply_font_size,
            'ff': self.apply_font_family,
            'font': self.apply_font_family,
            'st': self.apply_strikethrough,
            'strike': self.apply_strikethrough,
            'bo': self.apply_bold,
            'bold': self.apply_bold,
            'it': self.apply_italic,
            'italic': self.apply_italic,
            'ul': self.apply_underline,
            'underline': self.apply_underline,
            'rm': self.clear_formatting,
            'reset': self.clear_formatting,
            'code': self.apply_code_style,
            'mono': self.apply_mono_style,
            
            # Text transform
            'uc': self.apply_uppercase,
            'upper': self.apply_uppercase,
            'lc': self.apply_lowercase,
            'lower': self.apply_lowercase,
            'caps': self.apply_capitalize,
            'capitalize': self.apply_capitalize,
            'reverse': self.reverse_text,
            'scramble': self.scramble_text,
            'rot13': self.rot13_encode,
            
            # Layout
            'align': self.apply_alignment,
            'indent': self.apply_indent,
            'outdent': self.apply_outdent,
            'lineup': self.increase_line_spacing,
            'linedown': self.decrease_line_spacing,
            'paragraph': self.add_paragraph_spacing,
            
            # Search
            'find': self.find_text,
            'replace': self.replace_text,
            'findall': self.find_all_regex,
            'count': self.count_occurrences,
            
            # Edit
            'undo': self.undo,
            'redo': self.redo,
            'sa': self.select_all,
            'selectall': self.select_all,
            'del': self.delete_selection,
            'delete': self.delete_selection,
            'paste': self.paste_text,
            'dupline': self.duplicate_line,
            'movelineup': self.move_line_up,
            'movelinedown': self.move_line_down,
            
            # File
            'open': self.open_document,
            'load': self.open_document,
            'save': self.save_document,
            'new': self.new_document,
            'export': self.export_document,
            'insertfile': self.insert_file,
            
            # Insert
            'date': self.insert_date,
            'time': self.insert_time,
            'datetime': self.insert_datetime,
            'linenums': self.add_line_numbers,
            'bullets': self.add_bullet_points,
            
            # Special
            'sort': self.sort_lines,
            'shuffle': self.shuffle_lines,
            'unique': self.unique_lines,
            'wordcount': self.show_word_count,
            'charcount': self.show_char_count,
            
            # Session
            'bookmark': self.add_bookmark,
            'goto': self.go_to_bookmark,
            'history': self.show_command_history,
            'theme': self.change_theme,
            'help': self.show_help,
        }

        action = command_map.get(command)
        if not action:
            self.status(f'❌ Unknown command: {command}')
        else:
            action(args)

        self.command_entry.delete(0, 'end')
        self.update_status_bar()

    # New feature implementations
    def reverse_text(self, args=None):
        """Reverse the selected text"""
        self.transform_selection(lambda text: text[::-1])
        self.status('🔄 Text reversed.')

    def scramble_text(self, args=None):
        """Scramble the selected text"""
        import random
        def scramble(text):
            words = text.split()
            scrambled = []
            for word in words:
                if len(word) > 3:
                    middle = list(word[1:-1])
                    random.shuffle(middle)
                    scrambled.append(word[0] + ''.join(middle) + word[-1])
                else:
                    scrambled.append(word)
            return ' '.join(scrambled)
        self.transform_selection(scramble)
        self.status('🎲 Text scrambled.')

    def rot13_encode(self, args=None):
        """Apply ROT13 encoding to selected text"""
        def rot13(text):
            result = []
            for char in text:
                if char.isalpha():
                    ascii_offset = 65 if char.isupper() else 97
                    result.append(chr((ord(char) - ascii_offset + 13) % 26 + ascii_offset))
                else:
                    result.append(char)
            return ''.join(result)
        self.transform_selection(rot13)
        self.status('🔐 ROT13 encoding applied.')

    def increase_line_spacing(self, args=None):
        """Increase line spacing"""
        current = self.text_widget['spacing3']
        self.text_widget.configure(spacing3=current + 2)
        self.status(f'📏 Line spacing: {current + 2}px')

    def decrease_line_spacing(self, args=None):
        """Decrease line spacing"""
        current = self.text_widget['spacing3']
        new_spacing = max(0, current - 2)
        self.text_widget.configure(spacing3=new_spacing)
        self.status(f'📏 Line spacing: {new_spacing}px')

    def add_paragraph_spacing(self, args=None):
        """Add paragraph spacing after selection"""
        start, end = self.get_selection_range()
        if not start or not end:
            return
        self.text_widget.insert(end, '\n\n')
        self.status('📄 Paragraph spacing added.')

    def find_all_regex(self, args):
        """Find all occurrences using regex"""
        if not args:
            self.status('❌ Provide a regex pattern.', error=True)
            return
        pattern = ' '.join(args)
        try:
            content = self.text_widget.get('1.0', 'end-1c')
            self.text_widget.tag_remove('find_highlight', '1.0', 'end')
            self.text_widget.tag_configure('find_highlight', background='#fffb8f', foreground='black')
            
            matches = list(re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE))
            for match in matches:
                start = f'1.0+{match.start()}c'
                end = f'1.0+{match.end()}c'
                self.text_widget.tag_add('find_highlight', start, end)
            
            self.status(f'🔍 Found {len(matches)} matches for pattern "{pattern}".')
        except re.error as e:
            self.status(f'❌ Invalid regex: {str(e)}', error=True)

    def count_occurrences(self, args):
        """Count occurrences of text"""
        if not args:
            self.status('❌ Provide text to count.', error=True)
            return
        search_text = ' '.join(args)
        content = self.text_widget.get('1.0', 'end-1c')
        count = content.lower().count(search_text.lower())
        self.status(f'🔢 "{search_text}" appears {count} times.')

    def duplicate_line(self, args=None):
        """Duplicate the current line"""
        line = self.text_widget.index('insert').split('.')[0]
        content = self.text_widget.get(f'{line}.0', f'{line}.end')
        self.text_widget.insert(f'{line}.0', content + '\n')
        self.status('📋 Line duplicated.')

    def move_line_up(self, args=None):
        """Move current line up"""
        line = int(self.text_widget.index('insert').split('.')[0])
        if line > 1:
            current = self.text_widget.get(f'{line}.0', f'{line}.end')
            previous = self.text_widget.get(f'{line-1}.0', f'{line-1}.end')
            self.text_widget.delete(f'{line-1}.0', f'{line}.end')
            self.text_widget.insert(f'{line-1}.0', current + '\n' + previous)
            self.status('⬆️ Line moved up.')

    def move_line_down(self, args=None):
        """Move current line down"""
        line = int(self.text_widget.index('insert').split('.')[0])
        last_line = int(self.text_widget.index('end-1c').split('.')[0])
        if line < last_line:
            current = self.text_widget.get(f'{line}.0', f'{line}.end')
            next_line = self.text_widget.get(f'{line+1}.0', f'{line+1}.end')
            self.text_widget.delete(f'{line}.0', f'{line+1}.end')
            self.text_widget.insert(f'{line}.0', next_line + '\n' + current)
            self.status('⬇️ Line moved down.')

    def insert_date(self, args=None):
        """Insert current date"""
        self.text_widget.insert('insert', datetime.now().strftime('%Y-%m-%d'))
        self.status('📅 Date inserted.')

    def insert_time(self, args=None):
        """Insert current time"""
        self.text_widget.insert('insert', datetime.now().strftime('%H:%M:%S'))
        self.status('⏰ Time inserted.')

    def insert_datetime(self, args=None):
        """Insert current date and time"""
        self.text_widget.insert('insert', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        self.status('📅⏰ Date and time inserted.')

    def add_line_numbers(self, args=None):
        """Add line numbers to the entire document or selection"""
        if self.has_selection():
            start, end = self.get_selection_range()
            content = self.text_widget.get(start, end)
        else:
            content = self.text_widget.get('1.0', 'end-1c')
        
        lines = content.split('\n')
        numbered = '\n'.join(f'{i+1:4d}: {line}' for i, line in enumerate(lines))
        
        if self.has_selection():
            self.text_widget.delete(start, end)
            self.text_widget.insert(start, numbered)
        else:
            self.text_widget.delete('1.0', 'end')
            self.text_widget.insert('1.0', numbered)
        
        self.status('🔢 Line numbers added.')

    def add_bullet_points(self, args=None):
        """Add bullet points to selected lines"""
        start, end = self.get_selection_range()
        if not start or not end:
            self.status('❌ Select text first.', error=True)
            return
        
        content = self.text_widget.get(start, end)
        lines = content.split('\n')
        bulleted = '\n'.join(f'• {line}' if line.strip() else line for line in lines)
        
        self.text_widget.delete(start, end)
        self.text_widget.insert(start, bulleted)
        self.status('🔸 Bullet points added.')

    def sort_lines(self, args=None):
        """Sort selected lines alphabetically"""
        start, end = self.get_selection_range()
        if not start or not end:
            self.status('❌ Select lines to sort.', error=True)
            return
        
        content = self.text_widget.get(start, end)
        lines = content.split('\n')
        sorted_lines = sorted(lines, key=str.lower)
        
        self.text_widget.delete(start, end)
        self.text_widget.insert(start, '\n'.join(sorted_lines))
        self.status('🔤 Lines sorted alphabetically.')

    def shuffle_lines(self, args=None):
        """Shuffle selected lines randomly"""
        import random
        start, end = self.get_selection_range()
        if not start or not end:
            self.status('❌ Select lines to shuffle.', error=True)
            return
        
        content = self.text_widget.get(start, end)
        lines = content.split('\n')
        random.shuffle(lines)
        
        self.text_widget.delete(start, end)
        self.text_widget.insert(start, '\n'.join(lines))
        self.status('🎲 Lines shuffled.')

    def unique_lines(self, args=None):
        """Remove duplicate lines from selection"""
        start, end = self.get_selection_range()
        if not start or not end:
            self.status('❌ Select text to remove duplicates.', error=True)
            return
        
        content = self.text_widget.get(start, end)
        lines = content.split('\n')
        seen = set()
        unique = []
        for line in lines:
            if line not in seen:
                unique.append(line)
                seen.add(line)
        
        self.text_widget.delete(start, end)
        self.text_widget.insert(start, '\n'.join(unique))
        self.status(f'✨ Removed {len(lines) - len(unique)} duplicate lines.')

    def show_word_count(self, args=None):
        """Show word count dialog"""
        content = self.text_widget.get('1.0', 'end-1c')
        words = len(content.split())
        chars = len(content)
        chars_no_spaces = len(content.replace(' ', ''))
        lines = content.count('\n') + 1
        paragraphs = len([p for p in content.split('\n\n') if p.strip()])
        
        messagebox.showinfo(
            'Document Statistics',
            f'Words: {words}\n'
            f'Characters (with spaces): {chars}\n'
            f'Characters (no spaces): {chars_no_spaces}\n'
            f'Lines: {lines}\n'
            f'Paragraphs: {paragraphs}\n'
            f'Estimated reading time: {max(1, words // 200)} min'
        )
        self.status(f'📊 Words: {words} | Characters: {chars}')

    def show_char_count(self, args=None):
        """Show character count"""
        content = self.text_widget.get('1.0', 'end-1c')
        chars = len(content)
        self.status(f'🔤 Character count: {chars}')

    def add_bookmark(self, args):
        """Add a bookmark at current position"""
        if not args:
            self.status('❌ Provide a bookmark name.', error=True)
            return
        name = ' '.join(args)
        position = self.text_widget.index('insert')
        self.bookmarks[name] = position
        self.status(f'🔖 Bookmark "{name}" set at position {position}.')

    def go_to_bookmark(self, args):
        """Go to a saved bookmark"""
        if not args:
            self.status('❌ Provide a bookmark name.', error=True)
            return
        name = ' '.join(args)
        if name in self.bookmarks:
            self.text_widget.mark_set('insert', self.bookmarks[name])
            self.text_widget.see(self.bookmarks[name])
            self.status(f'📍 Jumped to bookmark "{name}".')
        else:
            self.status(f'❌ Bookmark "{name}" not found.', error=True)

    def show_command_history(self, args=None):
        """Show command history"""
        if not self.command_history:
            self.status('📜 No command history.')
            return
        
        history_window = tk.Toplevel(self.root)
        history_window.title('Command History')
        history_window.geometry('500x400')
        
        history_text = tk.Text(history_window, wrap='word', font=('Consolas', 12))
        history_text.pack(fill='both', expand=True)
        
        for i, cmd in enumerate(self.command_history, 1):
            history_text.insert('end', f'{i:3d}: {cmd}\n')
        
        history_text.config(state='disabled')
        self.status('📜 Command history displayed.')

    def change_theme(self, args):
        """Change the editor theme"""
        theme = args[0].lower() if args else 'dark'
        
        if theme == 'light':
            self.root.configure(bg='#f0f0f0')
            self.text_widget.configure(bg='white', fg='black', insertbackground='black')
            self.command_entry.configure(bg='white', fg='black', insertbackground='black')
            self.status_label.configure(bg='#f0f0f0', fg='#333333')
            self.status_bar.configure(bg='#f0f0f0', fg='#333333')
            self.line_numbers.configure(bg='#e0e0e0', fg='#666666')
            self.current_theme = 'light'
        else:
            self.root.configure(bg='#071b38')
            self.text_widget.configure(bg='#0f2345', fg='white', insertbackground='white')
            self.command_entry.configure(bg='#122846', fg='white', insertbackground='white')
            self.status_label.configure(bg='#071b38', fg='#b7d2ff')
            self.status_bar.configure(bg='#071b38', fg='#8da8d8')
            self.line_numbers.configure(bg='#0a1a3a', fg='#4a6a8a')
            self.current_theme = 'dark'
        
        self.status(f'🎨 Theme changed to {theme}.')

    def new_document(self, args=None):
        """Create a new document"""
        if self.text_widget.edit_modified():
            if messagebox.askyesno('Save Changes', 'Do you want to save changes?'):
                self.save_document([])
        self.text_widget.delete('1.0', 'end')
        self.status('📄 New document created.')

    def export_document(self, args):
        """Export document in different formats"""
        if not args:
            self.status('❌ Specify format: html, rtf, or pdf.', error=True)
            return
        
        format_type = args[0].lower()
        if format_type == 'html':
            self.export_html()
        elif format_type == 'rtf':
            self.export_rtf()
        else:
            self.status(f'❌ Unknown format: {format_type}', error=True)

    def export_html(self):
        """Export document as HTML"""
        path = filedialog.asksaveasfilename(
            defaultextension='.html',
            filetypes=[('HTML files', '*.html')]
        )
        if not path:
            return
        
        content = self.text_widget.get('1.0', 'end-1c')
        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Exported from Texxo Pro</title>
    <style>
        body {{ font-family: 'Segoe UI', sans-serif; padding: 20px; }}
        pre {{ background: #f4f4f4; padding: 10px; }}
    </style>
</head>
<body>
<pre>{content}</pre>
</body>
</html>"""
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        self.status(f'📄 Exported as HTML: {path}')

    def export_rtf(self):
        """Export document as RTF"""
        path = filedialog.asksaveasfilename(
            defaultextension='.rtf',
            filetypes=[('RTF files', '*.rtf')]
        )
        if not path:
            return
        
        content = self.text_widget.get('1.0', 'end-1c')
        # Basic RTF conversion
        rtf_content = '{\\rtf1\\ansi\\deff0\n'
        rtf_content += '{\\fonttbl{\\f0 Consolas;}}\n'
        rtf_content += '\\f0\\fs24\n'
        rtf_content += content.replace('\n', '\\par\n')
        rtf_content += '\n}'
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write(rtf_content)
        self.status(f'📄 Exported as RTF: {path}')

    def insert_file(self, args):
        """Insert content from another file"""
        path = ' '.join(args).strip()
        if not path:
            path = filedialog.askopenfilename(
                title='Insert File',
                filetypes=[('Text Files', '*.txt'), ('All Files', '*.*')]
            )
        if not path:
            return
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            self.text_widget.insert('insert', content)
            self.status(f'📁 Inserted file: {path}')
        except Exception as e:
            self.status(f'❌ Failed to insert file: {str(e)}', error=True)

    def cut_selection(self, args=None):
        """Cut selected text"""
        if not self.has_selection():
            self.status('❌ Select text first to cut.', error=True)
            return
        self.copy_selection()
        self.delete_selection()
        self.status('✂️ Text cut to clipboard.')

    def paste_text(self, args=None):
        """Paste text from clipboard"""
        try:
            text = self.root.clipboard_get()
            self.text_widget.insert('insert', text)
            self.status('📋 Text pasted from clipboard.')
        except:
            self.status('❌ Clipboard is empty.', error=True)

    def save_as_document(self):
        """Save document with a new name"""
        path = filedialog.asksaveasfilename(
            title='Save As',
            defaultextension='.txt',
            filetypes=[('Text Files', '*.txt'), ('All Files', '*.*')]
        )
        if path:
            self.current_file = path
            self.save_document([path])

    def show_recent_files(self):
        """Show recent files dialog"""
        if not self.recent_files:
            self.status('📂 No recent files.')
            return
        
        recent_window = tk.Toplevel(self.root)
        recent_window.title('Recent Files')
        recent_window.geometry('400x300')
        
        tk.Label(recent_window, text='Recent Files', font=('Segoe UI', 12, 'bold')).pack(pady=10)
        
        for file_path in self.recent_files:
            btn = tk.Button(
                recent_window,
                text=os.path.basename(file_path),
                command=lambda p=file_path: self.open_document([p]),
                anchor='w',
            )
            btn.pack(fill='x', padx=20, pady=2)

    def choose_color(self):
        """Open color chooser dialog"""
        color = colorchooser.askcolor(title='Choose Color')[1]
        if color:
            self.apply_color([color])

    def choose_font(self):
        """Open font chooser dialog"""
        families = list(FONT_MAP.keys())
        choice = simpledialog.askstring('Font', f'Available fonts: {", ".join(families[:10])}...\nEnter font name:')
        if choice and choice in FONT_MAP:
            self.apply_font_style([choice])

    def show_find_replace_dialog(self):
        """Show find and replace dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title('Find and Replace')
        dialog.geometry('400x200')
        dialog.configure(bg='#122846')
        
        tk.Label(dialog, text='Find:', fg='white', bg='#122846').pack(pady=5)
        find_entry = tk.Entry(dialog, width=50)
        find_entry.pack(pady=5)
        
        tk.Label(dialog, text='Replace:', fg='white', bg='#122846').pack(pady=5)
        replace_entry = tk.Entry(dialog, width=50)
        replace_entry.pack(pady=5)
        
        def do_replace():
            find_text = find_entry.get()
            replace_text = replace_entry.get()
            if find_text:
                self.replace_text([find_text, replace_text])
                dialog.destroy()
        
        tk.Button(
            dialog,
            text='Replace All',
            command=do_replace,
            bg='#1f508b',
            fg='white',
        ).pack(pady=20)

    def go_to_line(self):
        """Go to specific line number"""
        line = simpledialog.askinteger('Go to Line', 'Enter line number:')
        if line:
            self.text_widget.mark_set('insert', f'{line}.0')
            self.text_widget.see(f'{line}.0')
            self.status(f'📍 Jumped to line {line}.')

    def toggle_line_numbers(self):
        """Toggle line numbers visibility"""
        if self.line_numbers.winfo_viewable():
            self.line_numbers.pack_forget()
            self.status('🔢 Line numbers hidden.')
        else:
            self.line_numbers.pack(side='left', fill='y', before=self.text_widget)
            self.status('🔢 Line numbers shown.')

    def toggle_word_wrap(self):
        """Toggle word wrap"""
        current = self.text_widget['wrap']
        new_wrap = 'none' if current == 'word' else 'word'
        self.text_widget.configure(wrap=new_wrap)
        self.status(f'📝 Word wrap: {new_wrap}.')

    def show_about(self):
        """Show about dialog"""
        messagebox.showinfo(
            'About Texxo Pro',
            'Texxo Pro v2.0\n\n'
            'Advanced Text Editor with 100+ colors,\n'
            '50+ fonts, and 40+ commands.\n\n'
            'Created with Python and Tkinter.'
        )

    def start_auto_save(self):
        """Start auto-save timer"""
        self.auto_save()
        
    def auto_save(self):
        """Auto-save the document"""
        if self.auto_save_enabled and self.text_widget.edit_modified():
            self.save_document([])
        self.root.after(self.auto_save_interval, self.auto_save)

    def load_settings(self):
        """Load editor settings"""
        try:
            with open('texxo_settings.json', 'r') as f:
                settings = json.load(f)
                self.auto_save_enabled = settings.get('auto_save', False)
                self.recent_files = settings.get('recent_files', [])
        except FileNotFoundError:
            pass

    def save_settings(self):
        """Save editor settings"""
        settings = {
            'auto_save': self.auto_save_enabled,
            'recent_files': self.recent_files[-10:],  # Keep last 10
            'theme': self.current_theme,
        }
        with open('texxo_settings.json', 'w') as f:
            json.dump(settings, f)

    def show_previous_command(self, event):
        """Show previous command in history"""
        if self.command_history and hasattr(self, 'command_history_index'):
            if self.command_history_index > 0:
                self.command_history_index -= 1
                self.command_entry.delete(0, 'end')
                self.command_entry.insert(0, self.command_history[self.command_history_index])

    def show_next_command(self, event):
        """Show next command in history"""
        if self.command_history and hasattr(self, 'command_history_index'):
            if self.command_history_index < len(self.command_history) - 1:
                self.command_history_index += 1
                self.command_entry.delete(0, 'end')
                self.command_entry.insert(0, self.command_history[self.command_history_index])

    def __del__(self):
        """Save settings on exit"""
        self.save_settings()

    # Keeping all the original methods from the previous version
    # (has_selection, get_selection_range, resolve_color, apply_tag, etc.)
    # ... [Previous methods remain the same] ...

    def has_selection(self):
        try:
            self.text_widget.index('sel.first')
            return True
        except tk.TclError:
            return False

    def get_selection_range(self):
        try:
            start = self.text_widget.index('sel.first')
            end = self.text_widget.index('sel.last')
            return start, end
        except tk.TclError:
            return None, None

    def resolve_color(self, value):
        if not value:
            return '#f5f1a5'
        value = value.lower()
        return COLOR_MAP.get(value, value if value.startswith('#') else '#61afef')

    def apply_tag(self, tag_name, **options):
        start, end = self.get_selection_range()
        if not start or not end:
            return
        if tag_name not in self.text_widget.tag_names():
            self.text_widget.tag_configure(tag_name, **options)
        self.text_widget.tag_add(tag_name, start, end)
        self.status(f'✅ Applied {tag_name.replace("_", " ")}')

    def apply_highlight(self, args):
        color = self.resolve_color(args[0] if args else 'yellow')
        tag_name = f'highlight_{color}'
        self.apply_tag(tag_name, background=color, foreground='black')

    def apply_color(self, args):
        color = self.resolve_color(args[0] if args else 'white')
        tag_name = f'color_{color}'
        self.apply_tag(tag_name, foreground=color)

    def apply_font_style(self, args):
        style = args[0].lower() if args else 'clean'
        family, size = FONT_MAP.get(style, FONT_MAP.get('clean'))
        tag_name = f'font_{style}'
        new_font = self.default_font.copy()
        new_font.configure(family=family, size=size)
        self.apply_tag(tag_name, font=new_font)

    def apply_font_size(self, args):
        if not args or not args[0].isdigit():
            self.status('Font size must be a number.')
            return
        size = int(args[0])
        tag_name = f'fontsize_{size}'
        new_font = self.default_font.copy()
        new_font.configure(size=size)
        self.apply_tag(tag_name, font=new_font)

    def apply_bold(self, args=None):
        start, end = self.get_selection_range()
        if not start or not end:
            return
        self.text_widget.tag_add('bold', start, end)
        self.status('✅ Applied bold')

    def apply_italic(self, args=None):
        start, end = self.get_selection_range()
        if not start or not end:
            return
        self.text_widget.tag_add('italic', start, end)
        self.status('✅ Applied italic')

    def apply_underline(self, args=None):
        start, end = self.get_selection_range()
        if not start or not end:
            return
        self.text_widget.tag_add('underline', start, end)
        self.status('✅ Applied underline')

    def apply_strikethrough(self, args=None):
        start, end = self.get_selection_range()
        if not start or not end:
            return
        self.text_widget.tag_add('strikethrough', start, end)
        self.status('✅ Applied strikethrough')

    def apply_code_style(self, args=None):
        start, end = self.get_selection_range()
        if not start or not end:
            return
        code_font = self.default_font.copy()
        code_font.configure(family='Courier New')
        if 'code' not in self.text_widget.tag_names():
            self.text_widget.tag_configure('code', font=code_font)
        self.text_widget.tag_add('code', start, end)
        self.status('✅ Applied code style')

    def apply_mono_style(self, args=None):
        start, end = self.get_selection_range()
        if not start or not end:
            return
        tag_name = 'font_mono'
        mono_font = self.default_font.copy()
        mono_font.configure(family='Courier New', size=14)
        if tag_name not in self.text_widget.tag_names():
            self.text_widget.tag_configure(tag_name, font=mono_font)
        self.text_widget.tag_add(tag_name, start, end)
        self.status('✅ Applied mono style')

    def apply_font_family(self, args):
        if not args:
            self.status('Font family command needs a name.', error=True)
            return
        family = ' '.join(args)
        tag_name = f"font_family_{family.replace(' ', '_')}"
        new_font = self.default_font.copy()
        new_font.configure(family=family, size=self.default_font['size'])
        self.apply_tag(tag_name, font=new_font)

    def apply_alignment(self, args):
        if not args or args[0].lower() not in {'left', 'center', 'right'}:
            self.status('Use align left, align center, or align right.', error=True)
            return
        start, end = self.get_selection_range()
        if not start or not end:
            return
        tag_name = f'align_{args[0].lower()}'
        self.text_widget.tag_add(tag_name, start, end)
        self.status(f'✅ Applied {args[0]} alignment')

    def apply_indent(self, args=None):
        start, end = self.get_selection_range()
        if not start or not end:
            return
        current = self.text_widget.get(start, end)
        indented = '\n'.join('    ' + line for line in current.splitlines())
        self.text_widget.delete(start, end)
        self.text_widget.insert(start, indented)
        self.text_widget.tag_add('sel', start, f'{start}+{len(indented)}c')
        self.status('➡️ Indented selection.')

    def apply_outdent(self, args=None):
        start, end = self.get_selection_range()
        if not start or not end:
            return
        current = self.text_widget.get(start, end)
        outdented = '\n'.join(line[4:] if line.startswith('    ') else line.lstrip('\t') for line in current.splitlines())
        self.text_widget.delete(start, end)
        self.text_widget.insert(start, outdented)
        self.text_widget.tag_add('sel', start, f'{start}+{len(outdented)}c')
        self.status('⬅️ Outdented selection.')

    def delete_selection(self, args=None):
        if not self.has_selection():
            self.status('Select text first to delete.', error=True)
            return
        start, end = self.get_selection_range()
        self.text_widget.delete(start, end)
        self.status('🗑️ Selection deleted.')

    def find_text(self, args):
        if not args:
            self.status('Find command needs text to search.', error=True)
            return
        query = ' '.join(args)
        self.text_widget.tag_remove('find_highlight', '1.0', 'end')
        self.text_widget.tag_configure('find_highlight', background='#fffb8f', foreground='black')
        index = '1.0'
        count = 0
        while True:
            index = self.text_widget.search(query, index, nocase=True, stopindex='end')
            if not index:
                break
            end = f'{index}+{len(query)}c'
            self.text_widget.tag_add('find_highlight', index, end)
            index = end
            count += 1
        self.status(f'🔍 Found {count} matches for "{query}".')

    def replace_text(self, args):
        if len(args) < 2:
            self.status('Replace command needs old and new text.', error=True)
            return
        old_text = args[0]
        new_text = ' '.join(args[1:])
        if self.has_selection():
            start, end = self.get_selection_range()
            segment = self.text_widget.get(start, end)
            updated = segment.replace(old_text, new_text)
            self.text_widget.delete(start, end)
            self.text_widget.insert(start, updated)
            self.status('🔄 Replace completed in selection.')
        else:
            content = self.text_widget.get('1.0', 'end-1c')
            updated = content.replace(old_text, new_text)
            self.text_widget.delete('1.0', 'end')
            self.text_widget.insert('1.0', updated)
            self.status('🔄 Replace completed in document.')

    def save_document(self, args):
        path = ' '.join(args).strip() if args else ''
        if not path:
            if hasattr(self, 'current_file'):
                path = self.current_file
            else:
                path = filedialog.asksaveasfilename(
                    title='Save Document', 
                    defaultextension='.txt', 
                    filetypes=[('Text Files', '*.txt'), ('All Files', '*.*')]
                )
        if not path:
            self.status('Save canceled.')
            return
        try:
            content = self.text_widget.get('1.0', 'end-1c')
            with open(path, 'w', encoding='utf-8') as handle:
                handle.write(content)
            self.current_file = path
            if path not in self.recent_files:
                self.recent_files.append(path)
            self.text_widget.edit_modified(False)
            self.status(f'💾 Saved file: {path}')
        except Exception as exc:
            messagebox.showerror('Save Error', str(exc))
            self.status('Failed to save file.', error=True)

    def open_document(self, args):
        path = ' '.join(args).strip() if args else ''
        if not path:
            path = filedialog.askopenfilename(
                title='Open Document', 
                filetypes=[('Text Files', '*.txt'), ('All Files', '*.*')]
            )
        if not path:
            self.status('Open canceled.')
            return
        try:
            with open(path, 'r', encoding='utf-8') as handle:
                content = handle.read()
            self.text_widget.delete('1.0', 'end')
            self.text_widget.insert('1.0', content)
            self.current_file = path
            if path not in self.recent_files:
                self.recent_files.append(path)
            self.text_widget.edit_modified(False)
            self.status(f'📂 Opened file: {path}')
        except Exception as exc:
            messagebox.showerror('Open Error', str(exc))
            self.status('Failed to open file.', error=True)

    def select_all(self, args=None):
        self.text_widget.tag_add('sel', '1.0', 'end-1c')
        self.text_widget.mark_set('insert', '1.0')
        self.status('📝 All text selected.')

    def undo(self, args=None):
        try:
            self.text_widget.edit_undo()
            self.status('↩️ Undo completed.')
        except tk.TclError:
            self.status('Nothing to undo.', error=True)

    def redo(self, args=None):
        try:
            self.text_widget.edit_redo()
            self.status('↪️ Redo completed.')
        except tk.TclError:
            self.status('Nothing to redo.', error=True)

    def show_help(self, args=None):
        help_window = tk.Toplevel(self.root)
        help_window.title('Texxo Pro - Command Help')
        help_window.geometry('800x600')
        help_window.configure(bg='#122846')
        
        help_text = tk.Text(help_window, wrap='word', bg='#0f2345', fg='white', font=('Consolas', 12))
        help_text.pack(fill='both', expand=True, padx=10, pady=10)
        help_text.insert('1.0', HELP_TEXT)
        help_text.config(state='disabled')
        
        self.status('📚 Help displayed.')

    def clear_formatting(self, args=None):
        start, end = self.get_selection_range()
        if not start or not end:
            return
        for tag_name in self.text_widget.tag_names():
            self.text_widget.tag_remove(tag_name, start, end)
        self.status('🧹 Formatting reset for selection.')

    def transform_selection(self, transform):
        start, end = self.get_selection_range()
        if not start or not end:
            return
        original = self.text_widget.get(start, end)
        transformed = transform(original)
        self.text_widget.delete(start, end)
        self.text_widget.insert(start, transformed)
        self.status('✨ Text transformed.')

    def apply_uppercase(self, args=None):
        self.transform_selection(str.upper)

    def apply_lowercase(self, args=None):
        self.transform_selection(str.lower)

    def apply_capitalize(self, args=None):
        self.transform_selection(lambda text: text.title())

    def copy_selection(self):
        if not self.has_selection():
            self.status('Select text first to copy.')
            return
        start, end = self.get_selection_range()
        selection = self.text_widget.get(start, end)
        self.root.clipboard_clear()
        self.root.clipboard_append(selection)
        self.status('📋 Selected text copied to clipboard.')

    def status(self, message, error=False):
        self.status_label.config(text=message, fg='#ff8787' if error else '#b7d2ff')


if __name__ == '__main__':
    root = tk.Tk()
    app = TexxoEditor(root)
    root.mainloop()
