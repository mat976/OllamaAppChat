import os
import tkinter as tk
import tkinter.filedialog as filedialog
import subprocess
import sys
import pyperclip
import customtkinter as ctk
from CTkMessagebox import CTkMessagebox

class CommandPalette:
    def __init__(self, master, app):
        self.master = master
        self.app = app
        self.commands = {
            "Code Commands": [
                ("📋 Copy Last Response", self.copy_last_response),
                ("🔍 Search Code", self.search_code),
                ("📝 Open Text Editor", self.open_text_editor),
                ("💻 Open Terminal", self.open_terminal),
                ("🐍 Run Python Script", self.run_python_script),
                ("📂 Open Project Folder", self.open_project_folder)
            ],
            "Chat Management": [
                ("🗑️ Clear Current Chat", self.clear_current_chat),
                ("💾 Export Chat", self.export_chat),
                ("📊 Chat Statistics", self.show_chat_stats)
            ]
        }
        
        self.palette_window = None

    def show_command_palette(self, event=None):
        """Show the command palette"""
        if self.palette_window and tk.Toplevel.winfo_exists(self.palette_window):
            self.palette_window.destroy()
            return

        # Create a new top-level window
        self.palette_window = ctk.CTkToplevel(self.master)
        self.palette_window.title("Command Palette")
        self.palette_window.geometry("500x400")
        self.palette_window.attributes('-topmost', True)

        # Search entry
        search_var = tk.StringVar()
        search_var.trace("w", lambda name, index, mode, sv=search_var: self.filter_commands(sv))
        search_entry = ctk.CTkEntry(
            self.palette_window, 
            placeholder_text="Search commands...",
            textvariable=search_var
        )
        search_entry.pack(padx=10, pady=10, fill="x")
        search_entry.focus()

        # Commands list
        self.commands_list = ctk.CTkScrollableFrame(self.palette_window)
        self.commands_list.pack(padx=10, pady=10, fill="both", expand=True)

        self.populate_commands(self.commands)

        # Bind return key to execute selected command
        self.palette_window.bind("<Return>", self.execute_selected_command)
        self.palette_window.bind("<Escape>", lambda e: self.palette_window.destroy())

    def populate_commands(self, commands_dict):
        """Populate the command list"""
        for category, category_commands in commands_dict.items():
            category_label = ctk.CTkLabel(
                self.commands_list, 
                text=category, 
                font=ctk.CTkFont(weight="bold")
            )
            category_label.pack(anchor="w", padx=5, pady=(10, 5))

            for label, command in category_commands:
                cmd_button = ctk.CTkButton(
                    self.commands_list, 
                    text=label, 
                    anchor="w", 
                    command=lambda c=command: self.execute_command(c),
                    fg_color="transparent",
                    hover_color="gray"
                )
                cmd_button.pack(fill="x", padx=5, pady=2)

    def filter_commands(self, search_var):
        """Filter commands based on search input"""
        search_term = search_var.get().lower()
        
        # Destroy and recreate commands list
        for widget in self.commands_list.winfo_children():
            widget.destroy()

        filtered_commands = {}
        for category, category_commands in self.commands.items():
            matching_commands = [
                (label, cmd) for label, cmd in category_commands 
                if search_term in label.lower()
            ]
            if matching_commands:
                filtered_commands[category] = matching_commands

        self.populate_commands(filtered_commands)

    def execute_selected_command(self, event=None):
        """Execute the first visible command"""
        # Get first button in the list
        buttons = [w for w in self.commands_list.winfo_children() if isinstance(w, ctk.CTkButton)]
        if buttons:
            buttons[0].invoke()
            self.palette_window.destroy()

    def execute_command(self, command):
        """Execute a specific command"""
        command()
        if self.palette_window:
            self.palette_window.destroy()

    def copy_last_response(self):
        """Copy the last AI response to clipboard"""
        last_response = self.app.get_last_response()
        if last_response:
            pyperclip.copy(last_response)
            CTkMessagebox(title="Copied", message="Last AI response copied to clipboard!")

    def search_code(self):
        """Open a code search dialog"""
        self.perform_search()

    def perform_search(self):
        """Perform a search in the project"""
        # Implement search functionality
        pass

    def open_text_editor(self):
        """Open default text editor"""
        subprocess.Popen(["notepad.exe"])

    def open_terminal(self):
        """Open Windows Terminal"""
        subprocess.Popen(["wt.exe"])

    def run_python_script(self):
        """Open file dialog to select and run a Python script"""
        script_path = filedialog.askopenfilename(
            title="Select Python Script", 
            filetypes=[("Python files", "*.py")]
        )
        if script_path:
            subprocess.Popen(["python", script_path])

    def open_project_folder(self):
        """Open the project folder in file explorer"""
        project_path = os.path.dirname(os.path.abspath(__file__))
        subprocess.Popen(f"explorer {project_path}")

    def clear_current_chat(self):
        """Clear the current chat"""
        self.app.clear_chat()

    def export_chat(self):
        """Export the current chat to a file"""
        if self.app.current_chat:
            export_path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt")]
            )
            if export_path:
                self.app.export_chat_to_file(export_path)

    def show_chat_stats(self):
        """Display chat statistics"""
        stats = self.app.get_chat_statistics()
        # Implement a way to display these stats, perhaps in a new window
        stats_text = "\n".join([f"{k}: {v}" for k, v in stats.items()])
        CTkMessagebox(title="Chat Statistics", message=stats_text)
