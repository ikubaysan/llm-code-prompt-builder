import tkinter as tk
from tkinter import filedialog, scrolledtext, Checkbutton, Label, Frame, Canvas, Scrollbar
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
        # Replace the username (the part after 'Users') with 'MyUsername'
        if 'Users' in parts and len(parts) > parts.index('Users') + 1:
            parts[parts.index('Users') + 1] = 'MyUsername'
        return '\\'.join(parts)

class LLMCodePromptBuilder(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()
        self.title("LLM Code Prompt Builder")
        self.geometry("1000x800")
        self.resizable(False, False)  # Disable resizing
        self.last_update = "N/A"
        self.file_entries = {}

        # Query input area
        self.query_frame = tk.Frame(self)
        self.query_frame.pack(side=tk.TOP, fill=tk.X)
        self.query_label = tk.Label(self.query_frame, text="Query:")
        self.query_label.pack(side=tk.LEFT)
        self.query_input = scrolledtext.ScrolledText(self.query_frame, height=5)
        self.query_input.pack(side=tk.LEFT, expand=True, fill=tk.X)

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
        self.drag_drop_label = tk.Label(self.drag_drop_frame, text="Drag Files Here", bg='light grey')
        self.drag_drop_label.pack(expand=True)

        # Add Select All and Deselect All buttons
        self.selection_buttons_frame = tk.Frame(self)
        self.selection_buttons_frame.pack(fill=tk.X)

        self.select_all_button = tk.Button(self.selection_buttons_frame, text="Select All", command=self.select_all)
        self.select_all_button.pack(side=tk.LEFT, padx=10)

        self.deselect_all_button = tk.Button(self.selection_buttons_frame, text="Deselect All", command=self.deselect_all)
        self.deselect_all_button.pack(side=tk.LEFT)

        # Enable drag and drop
        self.drag_drop_frame.drop_target_register(DND_FILES)
        self.drag_drop_frame.dnd_bind('<<Drop>>', self.drop)

        # Container for file list and scrollbar
        self.file_list_container = tk.Frame(self)
        self.file_list_container.pack(side="left", fill="both", expand=True)

        # File list area with checkboxes and labels
        self.file_list_canvas = Canvas(self.file_list_container, borderwidth=0)
        self.file_list_frame = Frame(self.file_list_canvas)
        self.file_list_scrollbar = Scrollbar(self.file_list_container, orient="vertical", command=self.file_list_canvas.yview)
        self.file_list_canvas.configure(yscrollcommand=self.file_list_scrollbar.set)

        # Bind mouse wheel event to the canvas
        self.file_list_canvas.bind("<MouseWheel>", self.on_mousewheel)
        # Propagate mouse wheel event from the frame to the canvas
        self.file_list_frame.bind("<MouseWheel>", lambda event: self.file_list_canvas.event_generate("<MouseWheel>", delta=event.delta))

        self.bind_to_mousewheel(self.file_list_canvas, self.file_list_frame)


        self.file_list_scrollbar.pack(side="right", fill="y")
        self.file_list_canvas.pack(side="left", fill="both", expand=True)
        self.file_list_canvas.create_window((0,0), window=self.file_list_frame, anchor="nw")

        self.file_list_frame.bind("<Configure>", self.on_frame_configure)

        self.update_button = tk.Button(self, text="Update Prompt", command=self.update_prompt)
        self.update_button.pack(side=tk.TOP, pady=0)

        # Text display area with label
        self.text_display_frame = tk.Frame(self, height=200)  # Set a specific height for the frame
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

        # Character and Token Counts labels
        self.char_count_label = tk.Label(self.stats_update_frame, text="Characters: 0")
        self.char_count_label.pack(side=tk.LEFT, padx=10)
        self.token_count_label = tk.Label(self.stats_update_frame, text="Tokens: 0")
        self.token_count_label.pack(side=tk.LEFT, padx=10)

        # Label for latest update timestamp
        self.update_timestamp_label = tk.Label(self.stats_update_frame, text="Latest Update: N/A")
        self.update_timestamp_label.pack(side=tk.RIGHT, padx=10)

        # Clipboard button
        self.clipboard_button = tk.Button(self, text="Copy to Clipboard", command=self.copy_to_clipboard)
        self.clipboard_button.pack(side=tk.BOTTOM, pady=10)

    def bind_to_mousewheel(self, canvas, frame):
        # Bind to the canvas
        canvas.bind("<MouseWheel>", lambda e: self.on_mousewheel(e, canvas))

        # Bind to all child widgets recursively
        for child in frame.winfo_children():
            self.bind_to_mousewheel(canvas, child)

    def on_mousewheel(self, event, widget):
        if os.name == 'nt':  # For Windows
            widget.yview_scroll(int(-1 * (event.delta / 120)), "units")
        else:  # For Unix/Linux
            if event.num == 4:
                widget.yview_scroll(-1, "units")
            elif event.num == 5:
                widget.yview_scroll(1, "units")

    def process_file_path(self, file_path):

        # if file_path is surrounded by double quotes or single quotes, remove them
        if (file_path.startswith('"') and file_path.endswith('"')) or (file_path.startswith("'") and file_path.endswith("'")):
            file_path = file_path[1:-1]

        normalized_path = os.path.normpath(file_path)  # Normalize the path
        if normalized_path in self.file_entries:
            return  # Skip this file as it's already added

        # Return if the path does not exist
        if not os.path.exists(normalized_path):
            return

        file_info = FileInfo(normalized_path)
        file_info.checkbox_frame = Frame(self.file_list_frame)
        file_info.checkbox = Checkbutton(file_info.checkbox_frame, variable=file_info.check_var, command=self.update_file_selection_count)
        file_info.checkbox.pack(side=tk.LEFT)
        file_info.label = Label(file_info.checkbox_frame, text=normalized_path, wraplength=250, justify='left')
        file_info.label.pack(side=tk.LEFT)
        file_info.label.bind("<Button-1>", lambda e, cb=file_info.checkbox: cb.invoke())
        file_info.checkbox_frame.pack(anchor='w', fill='x')
        self.file_entries[normalized_path] = file_info
        self.update_file_selection_count()

    def add_path(self, event=None):  # event parameter is added to handle the key press
        path = self.path_entry.get().strip()
        if path:
            self.process_file_path(path)
            self.path_entry.delete(0, tk.END)  # Clear the entry field

    def select_all(self):
        for file_info in self.file_entries.values():
            file_info.check_var.set(True)
        self.update_file_selection_count()

    def deselect_all(self):
        for file_info in self.file_entries.values():
            file_info.check_var.set(False)
        self.update_file_selection_count()

    def on_frame_configure(self, event=None):
        self.file_list_canvas.configure(scrollregion=self.file_list_canvas.bbox("all"))

    @staticmethod
    def parse_file_paths(data_string):
        file_paths = []

        if '{' in data_string and '}' in data_string:
            # Paths contain space(s), and are contained within braces in a single string.
            # eg. '{C:/Users/PC/Documents/1STRESS TESTING/RAM Test 1.1.0.0/ramtest.log}
            # {C:/Users/PC/Documents/1STRESS TESTING/RAM Test 1.1.0.0/README.txt}
            # {C:/Users/PC/Documents/1STRESS TESTING/RAM Test 1.1.0.0/settings.txt}'
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
            # A path does not contain a space; a space separates each path.
            # eg. 'C:/Users/PC/Desktop/misc/coding/repos/public/llm-code-prompt-builder/LLMCodePromptBuilder.py C:/Users/PC/Desktop/misc/coding/repos/public/llm-code-prompt-builder/README.md'
            file_paths = data_string.split()

        return file_paths

    def drop(self, event):
        # event.data looks like
        file_paths = self.parse_file_paths(event.data)
        for file_path in file_paths:
            self.process_file_path(file_path)

    def toggle_checkbox(self, check_var):
        check_var.set(not check_var.get())

    def copy_to_clipboard(self):
        self.clipboard_clear()
        self.clipboard_append(self.text_display.get(1.0, tk.END))

    def update_prompt(self):
        prompt_text = self.query_input.get("1.0", tk.END) + "\n\n"
        for file_info in self.file_entries.values():
            if file_info.check_var.get():
                with open(file_info.file_path, 'r') as file:
                    content = file.read()
                    # Use the censored path for the prompt text instead of the actual path
                    prompt_text += f"CONTENTS OF {file_info.censored_path}:\n\n{content}\n\n"

        self.text_display.config(state='normal')
        self.text_display.delete(1.0, tk.END)
        self.text_display.insert(tk.INSERT, prompt_text)
        self.text_display.config(state='disabled')

        # Update character and token counts
        self.update_counts(prompt_text)

        # Update timestamp
        self.last_update = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.update_timestamp_label.config(text=f"Latest Update: {self.last_update}")

    def update_counts(self, text):
        char_count = len(text)
        #token_count = len(nltk.word_tokenize(text))
        token_count = len(text.split())  # Simple word count as a token estimate
        self.char_count_label.config(text=f"Characters: {char_count}")
        self.token_count_label.config(text=f"Tokens: {token_count}")

    def update_file_selection_count(self):
        count = sum(file_info.check_var.get() for file_info in self.file_entries.values())
        self.file_selection_count_label.config(text=f"Selected Files: {count}")

if __name__ == "__main__":
    app = LLMCodePromptBuilder()
    app.mainloop()
