import tkinter as tk
from tkinter import filedialog, scrolledtext, Checkbutton
from tkinterdnd2 import DND_FILES, TkinterDnD

class LLMCodePromptBuilder(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()
        self.title("LLM Code Prompt Builder")
        self.geometry("1000x700")

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
        self.file_entries = {}

        self.update_button = tk.Button(self, text="Update Prompt", command=self.update_prompt)
        self.update_button.pack(side=tk.TOP, pady=10)

        # Text display area with label
        self.text_display_frame = tk.Frame(self)
        self.text_display_frame.pack(expand=True, fill=tk.BOTH)
        self.text_display_label = tk.Label(self.text_display_frame, text="Prompt:")
        self.text_display_label.pack()
        self.text_display = scrolledtext.ScrolledText(self.text_display_frame, state='disabled')
        self.text_display.pack(expand=True, fill=tk.BOTH)

        # Clipboard button
        self.clipboard_button = tk.Button(self, text="Copy to Clipboard", command=self.copy_to_clipboard)
        self.clipboard_button.pack(side=tk.BOTTOM)

    def drop(self, event):
        file_paths = event.data.split()
        for file_path in file_paths:
            check_var = tk.BooleanVar()
            checkbox_frame = tk.Frame(self.file_list_frame)
            checkbox = Checkbutton(checkbox_frame, variable=check_var)
            checkbox.pack(side=tk.LEFT)
            label = tk.Label(checkbox_frame, text=file_path, wraplength=250, justify='left')
            label.pack(side=tk.LEFT)
            label.bind("<Button-1>", lambda e, cv=check_var: self.toggle_checkbox(cv))
            checkbox_frame.pack(anchor='w', fill='x')
            self.file_entries[file_path] = (check_var, checkbox_frame)

    def toggle_checkbox(self, check_var):
        check_var.set(not check_var.get())

    def update_prompt(self):
        prompt_text = self.query_input.get("1.0", tk.END) + "\n\n"
        for file_path, (check_var, _) in self.file_entries.items():
            if check_var.get():
                with open(file_path, 'r') as file:
                    content = file.read()
                    prompt_text += f"CONTENTS OF {file_path}:\n\n{content}\n\n"

        self.text_display.config(state='normal')
        self.text_display.delete(1.0, tk.END)
        self.text_display.insert(tk.INSERT, prompt_text)
        self.text_display.config(state='disabled')

    def copy_to_clipboard(self):
        self.clipboard_clear()
        self.clipboard_append(self.text_display.get(1.0, tk.END))

if __name__ == "__main__":
    app = LLMCodePromptBuilder()
    app.mainloop()
