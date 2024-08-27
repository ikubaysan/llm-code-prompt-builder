import tkinter as tk
from tkinter import filedialog, scrolledtext, Checkbutton, Label, Frame, Canvas, Scrollbar, Entry
from tkinterdnd2 import DND_FILES, TkinterDnD
from datetime import datetime
import os

class FileInfo:
    def __init__(self, file_path):
        self.file_path = file_path
        self.check_var = tk.BooleanVar()
        self.censored_path = self.censor_username(file_path)

    @staticmethod
    def censor_username(path):
        parts = path.split('\\')
        if 'Users' in parts and len(parts) > parts.index('Users') + 1:
            parts[parts.index('Users') + 1] = 'MyUsername'
        return '\\'.join(parts)

class LLMCodePromptBuilder(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()
        self.title("LLM Code Prompt Builder")
        self.geometry("1000x800")
        self.resizable(False, False)
        self.last_update = "N/A"
        self.file_entries = {}

        # Query Section
        self.query_frame = tk.Frame(self)
        self.query_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)
        self.query_label = tk.Label(self.query_frame, text="Query:")
        self.query_label.pack(side=tk.LEFT)
        self.query_input = scrolledtext.ScrolledText(self.query_frame, height=5)
        self.query_input.pack(side=tk.LEFT, expand=True, fill=tk.X)

        # Separator
        self.add_separator()

        # File/Folder Selection Section
        self.options_frame = tk.Frame(self)
        self.options_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

        self.recursion_var = tk.BooleanVar(value=False)
        self.recursion_checkbox = Checkbutton(self.options_frame, text="Recursively Add Files in Subfolders", variable=self.recursion_var)
        self.recursion_checkbox.pack(side=tk.LEFT)

        self.whitelisted_extensions = ['py', 'cs', 'cpp']

        self.whitelist_label = tk.Label(self.options_frame, text="Whitelisted Extensions:")
        self.whitelist_label.pack(side=tk.LEFT, padx=(10, 0))
        self.whitelist_entry = tk.Entry(self.options_frame)
        self.whitelist_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.whitelist_entry.insert(0, ', '.join(self.whitelisted_extensions))

        # Manual Path Entry Area
        self.manual_entry_frame = tk.Frame(self)
        self.manual_entry_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)
        self.path_entry = tk.Entry(self.manual_entry_frame)
        self.path_entry.pack(side=tk.LEFT, expand=True, fill=tk.X)
        self.path_entry.bind('<Return>', self.add_path)
        self.add_path_button = tk.Button(self.manual_entry_frame, text="Add Path", command=self.add_path)
        self.add_path_button.pack(side=tk.RIGHT)

        # Drag and Drop Area
        self.drag_drop_frame = tk.Frame(self, height=100, width=1000, bg='light grey')
        self.drag_drop_frame.pack(side=tk.TOP, padx=10, pady=10)
        self.drag_drop_frame.pack_propagate(False)
        self.drag_drop_label = tk.Label(self.drag_drop_frame, text="Drag Files or Folders Here", bg='light grey')
        self.drag_drop_label.pack(expand=True)

        # Enable drag and drop for the frame
        self.drag_drop_frame.drop_target_register(DND_FILES)
        self.drag_drop_frame.dnd_bind('<<Drop>>', self.drop)

        # Buttons for file and folder selection
        self.button_frame = tk.Frame(self)
        self.button_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)
        self.file_button = tk.Button(self.button_frame, text="Select File", command=self.select_file)
        self.file_button.pack(side=tk.LEFT)
        self.folder_button = tk.Button(self.button_frame, text="Select Folder", command=self.select_folder)
        self.folder_button.pack(side=tk.LEFT, padx=5)

        # Separator
        self.add_separator()

        # Prompt Section
        self.selection_buttons_frame = tk.Frame(self)
        self.selection_buttons_frame.pack(fill=tk.X, pady=5)

        self.select_all_button = tk.Button(self.selection_buttons_frame, text="Select All", command=self.select_all)
        self.select_all_button.pack(side=tk.LEFT, padx=10)

        self.deselect_all_button = tk.Button(self.selection_buttons_frame, text="Deselect All",
                                             command=self.deselect_all)
        self.deselect_all_button.pack(side=tk.LEFT)

        self.remove_selected_button = tk.Button(self.selection_buttons_frame, text="Remove Selected",
                                                command=self.remove_selected)
        self.remove_selected_button.pack(side=tk.LEFT, padx=5)

        self.remove_all_button = tk.Button(self.selection_buttons_frame, text="Remove All", command=self.remove_all)
        self.remove_all_button.pack(side=tk.LEFT, padx=5)

        # Add Search Box
        self.search_frame = tk.Frame(self)
        self.search_frame.pack(fill=tk.X, pady=5)  # This is now packed directly after selection_buttons_frame

        self.search_label = tk.Label(self.search_frame, text="Search:")
        self.search_label.pack(side=tk.LEFT, padx=5)

        self.search_entry = tk.Entry(self.search_frame, width=50)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, padx=(0, 10))
        self.search_entry.bind("<KeyRelease>", self.filter_files)

        # Container for file list and scrollbar
        self.file_list_container = tk.Frame(self)
        self.file_list_container.pack(side="left", fill="both", expand=True)

        # File list area with checkboxes and labels
        self.file_list_canvas = Canvas(self.file_list_container, borderwidth=0)
        self.file_list_frame = Frame(self.file_list_canvas)
        self.file_list_scrollbar = Scrollbar(self.file_list_container, orient="vertical", command=self.file_list_canvas.yview)
        self.file_list_canvas.configure(yscrollcommand=self.file_list_scrollbar.set)

        self.file_list_scrollbar.pack(side="right", fill="y")
        self.file_list_canvas.pack(side="left", fill="both", expand=True)
        self.file_list_canvas.create_window((0, 0), window=self.file_list_frame, anchor="nw")

        self.file_list_frame.bind("<Configure>", self.on_frame_configure)

        # Update Button
        self.update_button = tk.Button(self, text="Update Prompt", command=self.update_prompt)
        self.update_button.pack(side=tk.TOP, pady=10)

        # Text display area with label
        self.text_display_frame = tk.Frame(self, height=200)
        self.text_display_frame.pack(fill=tk.BOTH)
        self.text_display_label = tk.Label(self.text_display_frame, text="Prompt:")
        self.text_display_label.pack()
        self.text_display = scrolledtext.ScrolledText(self.text_display_frame, state='disabled', height=14)
        self.text_display.pack(fill=tk.BOTH)

        # Stats and update frame
        self.stats_update_frame = tk.Frame(self)
        self.stats_update_frame.pack(fill=tk.X)

        # File Selection Count Label
        self.file_selection_count_label = tk.Label(self.stats_update_frame, text="Selected Files: 0")
        self.file_selection_count_label.pack(side=tk.LEFT, padx=10)

        # Character and Word Counts labels
        self.char_count_label = tk.Label(self.stats_update_frame, text="Characters: 0")
        self.char_count_label.pack(side=tk.LEFT, padx=10)
        self.word_count_label = tk.Label(self.stats_update_frame, text="Words: 0")
        self.word_count_label.pack(side=tk.LEFT, padx=10)

        # Label for latest update timestamp
        self.update_timestamp_label = tk.Label(self.stats_update_frame, text="Latest Update: N/A")
        self.update_timestamp_label.pack(side=tk.RIGHT, padx=10)

        # Clipboard button
        self.clipboard_button = tk.Button(self, text="Copy to Clipboard", command=self.copy_to_clipboard)
        self.clipboard_button.pack(side=tk.BOTTOM, pady=10)

    def remove_all(self):
        search_term = self.search_entry.get().lower()
        to_remove = [path for path, info in self.file_entries.items() if search_term in path.lower()]
        for path in to_remove:
            self.file_entries[path].checkbox_frame.destroy()
            del self.file_entries[path]
        self.update_file_selection_count()

    def add_separator(self):
        separator = tk.Frame(self, height=2, bd=1, relief=tk.SUNKEN)
        separator.pack(fill=tk.X, padx=5, pady=10)

    def process_file_path(self, file_path):
        if (file_path.startswith('"') and file_path.endswith('"')) or (file_path.startswith("'") and file_path.endswith("'")):
            file_path = file_path[1:-1]

        normalized_path = os.path.normpath(file_path)
        if normalized_path in self.file_entries:
            return

        if not os.path.exists(normalized_path):
            return

        if os.path.isdir(normalized_path):
            self.process_directory(normalized_path)
        else:
            self.add_file(normalized_path)

    def filter_files(self, event=None):
        search_term = self.search_entry.get().lower()

        # Clear current view
        for file_info in self.file_entries.values():
            file_info.checkbox_frame.pack_forget()

        # Sort the files alphabetically by their path
        sorted_paths = sorted(self.file_entries.keys())

        # Show only the files that match the search term
        for path in sorted_paths:
            file_info = self.file_entries[path]
            if search_term in file_info.file_path.lower():
                file_info.checkbox_frame.pack(anchor='w', fill='x')

        self.update_file_selection_count()

    def add_file(self, file_path):
        extension = os.path.splitext(file_path)[1].lower().lstrip('.')
        if self.whitelisted_extensions and extension not in self.whitelisted_extensions:
            return

        if file_path not in self.file_entries:  # Ensure no duplicates
            file_info = FileInfo(file_path)
            file_info.checkbox_frame = Frame(self.file_list_frame)
            file_info.checkbox = Checkbutton(file_info.checkbox_frame, variable=file_info.check_var,
                                             command=self.update_file_selection_count)
            file_info.checkbox.pack(side=tk.LEFT)
            file_info.label = Label(file_info.checkbox_frame, text=file_info.censored_path, wraplength=250,
                                    justify='left')
            file_info.label.pack(side=tk.LEFT)
            file_info.label.bind("<Button-1>", lambda e, cb=file_info.checkbox: cb.invoke())
            self.file_entries[file_path] = file_info
            self.filter_files()  # Update and sort the list after adding a file
            self.update_file_selection_count()

    def process_directory(self, dir_path):
        for root, dirs, files in os.walk(dir_path):
            for file_name in files:
                file_path = os.path.join(root, file_name)
                normalized_path = os.path.normpath(file_path)
                if normalized_path not in self.file_entries:
                    self.add_file(normalized_path)
            if not self.recursion_var.get():
                break

    def add_path(self, event=None):
        path = self.path_entry.get().strip()
        if path:
            self.process_file_path(path)
            self.path_entry.delete(0, tk.END)

    def select_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.process_file_path(file_path)

    def select_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.process_file_path(folder_path)

    def drop(self, event):
        file_paths = self.parse_file_paths(event.data)
        for file_path in file_paths:
            self.process_file_path(file_path)

    def update_prompt(self):
        whitelist_input = self.whitelist_entry.get().strip()
        self.whitelisted_extensions = [ext.strip().lower() for ext in whitelist_input.split(',') if ext.strip()]

        prompt_text = self.query_input.get("1.0", tk.END) + "\n\n"
        for file_info in self.file_entries.values():
            if file_info.check_var.get():
                with open(file_info.file_path, 'r') as file:
                    content = file.read()
                    prompt_text += f"CONTENTS OF {file_info.censored_path}:\n\n{content}\n\n"

        self.text_display.config(state='normal')
        self.text_display.delete(1.0, tk.END)
        self.text_display.insert(tk.INSERT, prompt_text)
        self.text_display.config(state='disabled')

        self.update_counts(prompt_text)
        self.last_update = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.update_timestamp_label.config(text=f"Latest Update: {self.last_update}")

    def update_counts(self, text):
        char_count = len(text)
        word_count = len(text.split())
        self.char_count_label.config(text=f"Characters: {char_count}")
        self.word_count_label.config(text=f"Words: {word_count}")

    def update_file_selection_count(self):
        count = sum(file_info.check_var.get() for file_info in self.file_entries.values())
        self.file_selection_count_label.config(text=f"Selected Files: {count}")

    def remove_selected(self):
        selected_files = [path for path, info in self.file_entries.items() if info.check_var.get()]
        for path in selected_files:
            self.file_entries[path].checkbox_frame.destroy()
            del self.file_entries[path]
        self.filter_files()  # Update and sort the list after removing a file
        self.update_file_selection_count()

    def on_frame_configure(self, event=None):
        self.file_list_canvas.configure(scrollregion=self.file_list_canvas.bbox("all"))

    @staticmethod
    def parse_file_paths(data_string):
        file_paths = []
        if '{' in data_string and '}' in data_string:
            current_path = ''
            inside_braces = False
            for char in data_string:
                if char == '{':
                    inside_braces = True
                    current_path = ''
                elif char == '}':
                    inside_braces = False
                    file_paths.append(current_path.strip())
                elif inside_braces:
                    current_path += char
        else:
            file_paths = data_string.split()
        return file_paths

    def copy_to_clipboard(self):
        self.clipboard_clear()
        self.clipboard_append(self.text_display.get(1.0, tk.END))

    def select_all(self):
        search_term = self.search_entry.get().lower()
        for file_info in self.file_entries.values():
            if search_term in file_info.file_path.lower():
                file_info.check_var.set(True)
        self.update_file_selection_count()

    def deselect_all(self):
        search_term = self.search_entry.get().lower()
        for file_info in self.file_entries.values():
            if search_term in file_info.file_path.lower():
                file_info.check_var.set(False)
        self.update_file_selection_count()


if __name__ == "__main__":
    app = LLMCodePromptBuilder()
    app.mainloop()