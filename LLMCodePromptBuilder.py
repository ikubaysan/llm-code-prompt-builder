import tkinter as tk
from tkinter import filedialog, scrolledtext, Checkbutton, Label, Frame
from tkinterdnd2 import DND_FILES, TkinterDnD
from datetime import datetime
import nltk

# Ensure NLTK tokenizers are downloaded
nltk.download('punkt')

class FileInfo:
    def __init__(self, file_path):
        self.file_path = file_path
        self.check_var = tk.BooleanVar()

class LLMCodePromptBuilder(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()
        self.title("LLM Code Prompt Builder")
        self.geometry("1000x700")
        self.last_update = "N/A"
        self.file_entries = {}

        # Query input area
        self.query_frame = tk.Frame(self)
        self.query_frame.pack(side=tk.TOP, fill=tk.X)
        self.query_label = tk.Label(self.query_frame, text="Query:")
        self.query_label.pack(side=tk.LEFT)
        self.query_input = scrolledtext.ScrolledText(self.query_frame, height=5)
        self.query_input.pack(side=tk.LEFT, expand=True, fill=tk.X)

        # Drag and Drop Area
        self.drag_drop_frame = tk.Frame(self, height=100, width=200, bg='light grey')
        self.drag_drop_frame.pack(side=tk.TOP, padx=10, pady=10)
        self.drag_drop_frame.pack_propagate(False)
        self.drag_drop_label = tk.Label(self.drag_drop_frame, text="Drag Files Here", bg='light grey')
        self.drag_drop_label.pack(expand=True)

        # Enable drag and drop
        self.drag_drop_frame.drop_target_register(DND_FILES)
        self.drag_drop_frame.dnd_bind('<<Drop>>', self.drop)

        # File list area with checkboxes and labels
        self.file_list_frame = tk.Frame(self)
        self.file_list_frame.pack(side=tk.LEFT, fill=tk.Y, expand=True)

        self.update_button = tk.Button(self, text="Update Prompt", command=self.update_prompt)
        self.update_button.pack(side=tk.TOP, pady=10)

        # Text display area with label
        self.text_display_frame = tk.Frame(self)
        self.text_display_frame.pack(expand=True, fill=tk.BOTH)
        self.text_display_label = tk.Label(self.text_display_frame, text="Prompt:")
        self.text_display_label.pack()
        self.text_display = scrolledtext.ScrolledText(self.text_display_frame, state='disabled')
        self.text_display.pack(expand=True, fill=tk.BOTH)

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

    def drop(self, event):
        file_paths = event.data.split()
        for file_path in file_paths:
            file_info = FileInfo(file_path)
            file_info.checkbox_frame = Frame(self.file_list_frame)
            file_info.checkbox = Checkbutton(file_info.checkbox_frame, variable=file_info.check_var, command=self.update_file_selection_count)
            file_info.checkbox.pack(side=tk.LEFT)
            file_info.label = Label(file_info.checkbox_frame, text=file_path, wraplength=250, justify='left')
            file_info.label.pack(side=tk.LEFT)
            file_info.label.bind("<Button-1>", lambda e, cb=file_info.checkbox: cb.invoke())
            file_info.checkbox_frame.pack(anchor='w', fill='x')
            self.file_entries[file_path] = file_info
        self.update_file_selection_count()

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
                    prompt_text += f"CONTENTS OF {file_info.file_path}:\n\n{content}\n\n"

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
        token_count = len(nltk.word_tokenize(text))
        self.char_count_label.config(text=f"Characters: {char_count}")
        self.token_count_label.config(text=f"Tokens: {token_count}")

    def update_file_selection_count(self):
        count = sum(file_info.check_var.get() for file_info in self.file_entries.values())
        self.file_selection_count_label.config(text=f"Selected Files: {count}")

if __name__ == "__main__":
    app = LLMCodePromptBuilder()
    app.mainloop()