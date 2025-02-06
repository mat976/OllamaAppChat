import os
import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
import queue
import threading
import tkinter as tk
import subprocess
import sys
import pyperclip
import tkinter.filedialog as filedialog

from chat_manager import ChatManager
from models import OllamaModelHandler, ModelChatThread

class OllamaChatApp:
    def __init__(self, root):
        # Configure appearance
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Main window setup
        self.root = root
        self.root.title("🤖 Ollama AI Chat")
        self.root.geometry("1200x800")  # Slightly reduced width
        self.root.minsize(1000, 600)

        # Chat management
        self.chat_manager = ChatManager()
        self.current_chat = None
        self.response_queue = queue.Queue()

        # Command Palette
        self.command_palette = CommandPalette(self.root, self)
        self.root.bind("<Control-p>", lambda event: self.command_palette.show_command_palette())

        # Main grid layout
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        # Main frame
        self.main_frame = ctk.CTkFrame(self.root, corner_radius=10)
        self.main_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=4)
        self.main_frame.grid_rowconfigure(0, weight=1)

        # Sidebar for chat list
        self.sidebar_frame = ctk.CTkFrame(self.main_frame, width=250, corner_radius=10)
        self.sidebar_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(2, weight=1)

        # Sidebar title
        self.sidebar_title = ctk.CTkLabel(
            self.sidebar_frame, 
            text="🤖 Chats", 
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.sidebar_title.grid(row=0, column=0, padx=10, pady=(10, 5))

        # Chat Management Buttons Frame
        self.chat_buttons_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        self.chat_buttons_frame.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        self.chat_buttons_frame.grid_columnconfigure((0,1), weight=1)

        # New Chat Button
        self.new_chat_button = ctk.CTkButton(
            self.chat_buttons_frame, 
            text="+ New Chat", 
            command=self.create_new_chat,
            corner_radius=20,
            width=120
        )
        self.new_chat_button.grid(row=0, column=0, padx=2, pady=2)

        # Clear Chats Button
        self.clear_chats_button = ctk.CTkButton(
            self.chat_buttons_frame, 
            text="🗑️", 
            command=self.clear_all_chats,
            corner_radius=20,
            width=50,
            fg_color="red",
            hover_color="darkred"
        )
        self.clear_chats_button.grid(row=0, column=1, padx=2, pady=2)

        # Chat List (now with a fixed height and no scrollbar by default)
        self.chat_list = ctk.CTkScrollableFrame(
            self.sidebar_frame, 
            corner_radius=10,
            height=500,  # Adjust as needed
            width=230   # Slightly less than sidebar width
        )
        self.chat_list.grid(row=2, column=0, padx=5, pady=5, sticky="nsew")

        # Chat Area
        self.chat_frame = ctk.CTkFrame(self.main_frame, corner_radius=10)
        self.chat_frame.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        self.chat_frame.grid_rowconfigure(0, weight=1)
        self.chat_frame.grid_columnconfigure(0, weight=1)

        # Chat Text Area with vertical scrollbar
        self.chat_text_frame = ctk.CTkFrame(self.chat_frame, fg_color="transparent")
        self.chat_text_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        self.chat_text_frame.grid_columnconfigure(0, weight=1)
        self.chat_text_frame.grid_rowconfigure(0, weight=1)

        # Scrollbar
        self.chat_text_scrollbar = ctk.CTkScrollbar(
            self.chat_text_frame, 
            orientation="vertical"
        )
        self.chat_text_scrollbar.grid(row=0, column=1, sticky="ns")

        # Chat Text with scrollbar
        self.chat_text = ctk.CTkTextbox(
            self.chat_text_frame, 
            state="disabled", 
            wrap="word",
            corner_radius=10,
            yscrollcommand=self.chat_text_scrollbar.set
        )
        self.chat_text.grid(row=0, column=0, sticky="nsew")
        
        # Configure scrollbar
        self.chat_text_scrollbar.configure(command=self.chat_text.yview)

        # Configure text tags for styling
        self.chat_text.tag_config("user_tag", foreground="light blue")
        self.chat_text.tag_config("ai_tag", foreground="light green")

        # Ensure scroll to bottom
        def scroll_to_bottom(event=None):
            self.chat_text.see("end")
        
        self.root.after(100, scroll_to_bottom)

        # Model Selection Frame
        self.model_frame = ctk.CTkFrame(self.chat_frame, fg_color="transparent")
        self.model_frame.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        self.model_frame.grid_columnconfigure(0, weight=1)

        # Model Selection Combo Box
        self.model_combo = ctk.CTkComboBox(
            self.model_frame, 
            state="readonly", 
            width=250  # Reduced width
        )
        self.model_combo.grid(row=0, column=0, padx=(0, 5), pady=5, sticky="ew")

        # Populate models
        self.populate_models()

        # Message Input Frame
        self.input_frame = ctk.CTkFrame(self.chat_frame, fg_color="transparent")
        self.input_frame.grid(row=2, column=0, padx=5, pady=5, sticky="ew")
        self.input_frame.grid_columnconfigure(0, weight=1)
        self.input_frame.grid_columnconfigure(1, weight=1)
        self.input_frame.grid_columnconfigure(2, weight=1)

        # Message Entry
        self.message_entry = ctk.CTkEntry(
            self.input_frame, 
            placeholder_text="Type your message...",
            width=500  # Reduced width
        )
        self.message_entry.grid(row=0, column=0, padx=(0, 5), pady=5, sticky="ew")
        self.message_entry.bind("<Return>", self.send_message)

        # Send Button
        self.send_button = ctk.CTkButton(
            self.input_frame, 
            text="Send", 
            command=self.send_message,
            width=80  # Reduced width
        )
        self.send_button.grid(row=0, column=1, padx=5, pady=5)

        # Command Palette Button
        self.command_palette_button = ctk.CTkButton(
            self.input_frame, 
            text="⌘", 
            command=self.command_palette.show_command_palette,
            width=50
        )
        self.command_palette_button.grid(row=0, column=2, padx=5, pady=5)

        # Load existing chats
        self.load_existing_chats()

        # Start response processing thread
        self.response_thread = threading.Thread(target=self.process_responses, daemon=True)
        self.response_thread.start()

        # Schedule periodic queue checking
        self.root.after(100, self.check_response_queue)

    def populate_models(self):
        """
        Populate the model selection combo box with available models
        """
        try:
            # Get available models from OllamaModelHandler
            models = OllamaModelHandler.get_available_models()
            
            if models:
                # Set the first model as default
                self.model_combo.configure(values=models)
                self.model_combo.set(models[0])
            else:
                # No models available
                self.model_combo.configure(values=["No models found"])
                self.model_combo.set("No models found")
        except Exception as e:
            # Handle any errors in model retrieval
            print(f"Error populating models: {e}")
            self.model_combo.configure(values=["Error loading models"])
            self.model_combo.set("Error loading models")

    def create_new_chat(self):
        """Create a new chat session with the currently selected model"""
        model = self.model_combo.get()
        new_chat = self.chat_manager.create_new_chat(model)
        
        # Immediately load the new chat
        self.current_chat = new_chat
        
        # Refresh chat list
        self.load_existing_chats()
        
        # Clear chat text area
        self.chat_text.configure(state="normal")
        self.chat_text.delete("1.0", "end")
        self.chat_text.configure(state="disabled")

    def load_existing_chats(self):
        """
        Load and display existing chats in a more user-friendly manner
        """
        # Clear existing chat list
        for widget in self.chat_list.winfo_children():
            widget.destroy()
        
        # Retrieve existing chats
        chats = self.chat_manager.list_chats()
        
        if not chats:
            # Show a placeholder when no chats exist
            no_chats_label = ctk.CTkLabel(
                self.chat_list, 
                text="No chats yet. Start a new chat!",
                text_color="gray"
            )
            no_chats_label.pack(pady=20)
            return
        
        # Create a more compact and visually appealing chat list
        for chat in chats:
            chat_frame = ctk.CTkFrame(
                self.chat_list, 
                fg_color="transparent"
            )
            chat_frame.pack(fill="x", padx=5, pady=3)
            
            # Chat title with truncation
            title = chat.get('title', 'Untitled Chat')
            if len(title) > 25:
                title = title[:25] + '...'
            
            chat_title = ctk.CTkLabel(
                chat_frame, 
                text=title, 
                anchor="w",
                font=ctk.CTkFont(size=12)
            )
            chat_title.pack(side="left", expand=True, fill="x")
            
            # Model badge
            model_badge = ctk.CTkLabel(
                chat_frame, 
                text=chat.get('model', 'Unknown'),
                fg_color="gray",
                text_color="white",
                corner_radius=10,
                width=60,
                height=20,
                font=ctk.CTkFont(size=10)
            )
            model_badge.pack(side="right", padx=5)
            
            # Make the entire frame clickable to select chat
            chat_frame.bind("<Button-1>", lambda e, c=chat: self.load_selected_chat(c))
            chat_title.bind("<Button-1>", lambda e, c=chat: self.load_selected_chat(c))
            model_badge.bind("<Button-1>", lambda e, c=chat: self.load_selected_chat(c))

    def load_selected_chat(self, chat):
        """
        Load a selected chat and display its messages
        """
        # Update current chat
        self.current_chat = chat
        
        # Clear existing chat text
        self.chat_text.configure(state="normal")
        self.chat_text.delete("1.0", "end")
        
        # Display chat messages
        for msg in chat.get('messages', []):
            role = msg['role']
            content = msg['content']
            
            # Determine tag based on role
            tag = "user_tag" if role == "user" else "ai_tag"
            
            # Insert message with appropriate styling
            self.chat_text.insert("end", f"{role.upper()}: ", tag)
            self.chat_text.insert("end", f"{content}\n\n")
        
        self.chat_text.configure(state="disabled")
        self.chat_text.see("end")
        
        # Update model selection to match chat's model
        if chat.get('model') in self.model_combo['values']:
            self.model_combo.set(chat['model'])

    def clear_all_chats(self):
        """Clear all existing chats with confirmation"""
        # Use CustomTkinter's message box for a modern look
        confirm = CTkMessagebox(
            title="Confirm Clear", 
            message="Are you sure you want to clear all chats?",
            icon="warning", 
            option_1="Yes", 
            option_2="No"
        )
        
        if confirm.get() == "Yes":
            # Clear chats through chat manager
            self.chat_manager.clear_all_chats()
            
            # Refresh chat list and current chat
            self.load_existing_chats()
            self.current_chat = None
            
            # Clear chat text area
            self.chat_text.configure(state="normal")
            self.chat_text.delete("1.0", "end")
            self.chat_text.configure(state="disabled")

    def delete_current_chat(self):
        """
        Delete the current chat session
        """
        if not self.current_chat:
            CTkMessagebox(
                title="Error", 
                message="No chat selected to delete.", 
                icon="cancel"
            )
            return

        # Create a confirmation dialog
        confirm = CTkMessagebox(
            title="Confirm Delete Chat", 
            message=f"Are you sure you want to delete this chat: {self.current_chat.get('title', 'Untitled Chat')}?",
            icon="warning", 
            option_1="Cancel", 
            option_2="Delete"
        )
        
        # Wait for user response
        response = confirm.get()
        
        if response == "Delete":
            # Delete the current chat
            self.chat_manager.delete_chat(self.current_chat['id'])
            
            # Remove the chat button from the list
            for widget in self.chat_list.winfo_children():
                if hasattr(widget, 'chat_id') and widget.chat_id == self.current_chat['id']:
                    widget.destroy()
                    break
            
            # Reset current chat
            self.current_chat = None
            
            # Clear chat text
            self.chat_text.configure(state="normal")
            self.chat_text.delete("1.0", "end")
            self.chat_text.configure(state="disabled")
            
            # Show confirmation
            CTkMessagebox(
                title="Chat Deleted", 
                message="The chat session has been deleted.", 
                icon="info"
            )

    def delete_specific_chat(self, chat):
        """
        Delete a specific chat session
        
        Args:
            chat (dict): Chat session to delete
        """
        # Create a confirmation dialog
        confirm = CTkMessagebox(
            title="Confirm Delete Chat", 
            message=f"Are you sure you want to delete this chat: {chat.get('title', 'Untitled Chat')}?",
            icon="warning", 
            option_1="Cancel", 
            option_2="Delete"
        )
        
        # Wait for user response
        response = confirm.get()
        
        if response == "Delete":
            # Delete the chat
            self.chat_manager.delete_chat(chat['id'])
            
            # Remove the chat button from the list
            for widget in self.chat_list.winfo_children():
                if hasattr(widget, 'chat_id') and widget.chat_id == chat['id']:
                    widget.destroy()
                    break
            
            # If the deleted chat was the current chat, reset
            if self.current_chat and self.current_chat['id'] == chat['id']:
                self.current_chat = None
                self.chat_text.configure(state="normal")
                self.chat_text.delete("1.0", "end")
                self.chat_text.configure(state="disabled")
            
            # Show confirmation
            CTkMessagebox(
                title="Chat Deleted", 
                message="The chat session has been deleted.", 
                icon="info"
            )

    def send_message(self, event=None):
        """Send a message in the current chat"""
        if not self.current_chat:
            CTkMessagebox(
                title="Error", 
                message="Please create a new chat first.", 
                icon="cancel"
            )
            return

        message = self.message_entry.get().strip()
        if not message:
            return

        # Clear input
        self.message_entry.delete(0, 'end')

        # Add user message to chat
        self.current_chat = self.chat_manager.add_message(
            self.current_chat, 'user', message
        )
        self.display_message('user', message)

        # Prepare messages for model
        messages = self.current_chat['messages']

        # Start chat thread
        thread = ModelChatThread(
            self.current_chat['model'], 
            messages, 
            self.response_queue
        )
        thread.start()

    def display_message(self, role, content, think_content=None):
        """
        Display a message in the chat text area
        
        Args:
            role (str): Message role (user/assistant)
            content (str): Message content
            think_content (str, optional): Internal thought content
        """
        self.chat_text.configure(state="normal")
        
        # Always insert at the end
        self.chat_text.insert("end", "\n")
        
        # Determine formatting based on role
        if role == 'user':
            self.chat_text.insert("end", f"You: {content}\n", "user_tag")
        else:
            # Insert AI message
            ai_message = f"AI: {content}\n"
            self.chat_text.insert("end", ai_message, "ai_tag")
            
            # Add think content button if available
            if think_content and think_content.strip():
                # Create a unique tag for this specific think button
                unique_tag = f"think_button_{id(think_content)}"
                
                # Insert think button text with unique tag
                think_button_text = " 💭 Thoughts "
                self.chat_text.insert("end", think_button_text, unique_tag)
                
                # Configure the unique tag
                self.chat_text.tag_config(unique_tag, 
                    foreground="white", 
                    background="gray"
                )
                
                # Bind events using lambda with unique tag
                self.chat_text.tag_bind(unique_tag, "<Button-1>", 
                    lambda event, tc=think_content: self._show_think_content(tc)
                )
                self.chat_text.tag_bind(unique_tag, "<Enter>", 
                    lambda event, tag=unique_tag: self._on_think_button_enter(tag)
                )
                self.chat_text.tag_bind(unique_tag, "<Leave>", 
                    lambda event, tag=unique_tag: self._on_think_button_leave(tag)
                )
        
        # Always add an extra newline and scroll to bottom
        self.chat_text.insert("end", "\n")
        self.chat_text.configure(state="disabled")
        self.chat_text.see("end")

    def _on_think_button_enter(self, tag):
        """
        Handle mouse enter event for think button
        
        Args:
            tag (str): Unique tag for the think button
        """
        self.chat_text.configure(cursor="hand2")
        self.chat_text.tag_config(tag, background="darkgray")

    def _on_think_button_leave(self, tag):
        """
        Handle mouse leave event for think button
        
        Args:
            tag (str): Unique tag for the think button
        """
        self.chat_text.configure(cursor="")
        self.chat_text.tag_config(tag, background="gray")

    def _show_think_content(self, think_content):
        """
        Show think content in a popup window
        
        Args:
            think_content (str): Internal thought content
        """
        # Create a new window for think content
        think_window = ctk.CTkToplevel(self.root)
        think_window.title("Internal Thoughts")
        think_window.geometry("500x300")
        
        # Text widget to display think content
        think_text = ctk.CTkTextbox(
            think_window, 
            state="normal", 
            wrap="word"
        )
        think_text.pack(padx=10, pady=10, fill="both", expand=True)
        
        # Insert think content
        think_text.insert("1.0", think_content)
        think_text.configure(state="disabled")

    def process_responses(self):
        """Process responses from the model in a separate thread"""
        while True:
            try:
                # Unpack the response with think content
                model, response, think_content, is_complete = self.response_queue.get()
                
                # Add AI response to current chat
                self.current_chat = self.chat_manager.add_message(
                    self.current_chat, 'assistant', response
                )
                
                # Save the chat
                self.chat_manager.save_chat(self.current_chat)
                
                # Display response in main thread
                self.root.after(0, self.display_message, 'assistant', response, think_content)
                
                self.response_queue.task_done()
            except Exception as e:
                print(f"Error processing response: {e}")

    def check_response_queue(self):
        """Check response queue periodically"""
        try:
            # Non-blocking check of the queue
            model, response, think_content, is_complete = self.response_queue.get_nowait()
            self.root.after(0, self.display_message, 'assistant', response, think_content)
        except queue.Empty:
            pass
        
        # Schedule next check
        self.root.after(100, self.check_response_queue)

    def clear_chat(self):
        """
        Clear the current chat text area
        """
        self.chat_text.configure(state="normal")
        self.chat_text.delete("1.0", "end")
        self.chat_text.configure(state="disabled")

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
    
    def show_command_palette(self):
        if self.palette_window and self.palette_window.winfo_exists():
            self.palette_window.lift()
            return
        
        self.palette_window = ctk.CTkToplevel(self.master)
        self.palette_window.title("🤖 Command Palette")
        self.palette_window.geometry("500x600")
        self.palette_window.resizable(False, False)
        
        # Title
        title = ctk.CTkLabel(
            self.palette_window, 
            text="🤖 Command Palette", 
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title.pack(pady=10)
        
        # Scrollable frame for commands
        command_frame = ctk.CTkScrollableFrame(
            self.palette_window, 
            width=480, 
            height=500
        )
        command_frame.pack(padx=10, pady=10)
        
        # Add command groups
        for group_name, commands in self.commands.items():
            group_label = ctk.CTkLabel(
                command_frame, 
                text=group_name, 
                font=ctk.CTkFont(size=14, weight="bold")
            )
            group_label.pack(pady=(10, 5), anchor="w")
            
            for cmd_name, cmd_func in commands:
                cmd_button = ctk.CTkButton(
                    command_frame, 
                    text=cmd_name, 
                    command=cmd_func,
                    anchor="w",
                    width=460
                )
                cmd_button.pack(pady=2, fill="x")
    
    def copy_last_response(self):
        if self.app.current_chat and self.app.current_chat['messages']:
            last_message = self.app.current_chat['messages'][-1]['content']
            pyperclip.copy(last_message)
            CTkMessagebox(title="Copied", message="Last AI response copied to clipboard!")
    
    def search_code(self):
        # Open a dialog to search code in the project
        search_window = ctk.CTkToplevel(self.master)
        search_window.title("🔍 Code Search")
        search_window.geometry("400x200")
        
        label = ctk.CTkLabel(search_window, text="Enter search term:")
        label.pack(pady=10)
        
        search_entry = ctk.CTkEntry(search_window, width=300)
        search_entry.pack(pady=10)
        
        def perform_search():
            term = search_entry.get()
            try:
                # Use ripgrep for fast code search
                result = subprocess.run(
                    ['rg', '-n', term, '.'], 
                    capture_output=True, 
                    text=True, 
                    cwd=os.path.dirname(os.path.abspath(__file__))
                )
                
                # Show results in a new window
                results_window = ctk.CTkToplevel(search_window)
                results_window.title(f"Search Results for '{term}'")
                results_window.geometry("600x400")
                
                results_text = ctk.CTkTextbox(results_window, wrap="word")
                results_text.pack(expand=True, fill="both", padx=10, pady=10)
                
                results_text.insert("1.0", result.stdout or "No results found.")
                results_text.configure(state="disabled")
            except Exception as e:
                CTkMessagebox(title="Error", message=f"Search failed: {str(e)}")
        
        search_button = ctk.CTkButton(search_window, text="Search", command=perform_search)
        search_button.pack(pady=10)
    
    def open_text_editor(self):
        subprocess.Popen(['notepad.exe'])
    
    def open_terminal(self):
        subprocess.Popen(['cmd.exe'])
    
    def run_python_script(self):
        # Open file dialog to select Python script
        script_path = filedialog.askopenfilename(
            title="Select Python Script", 
            filetypes=[("Python Files", "*.py")]
        )
        
        if script_path:
            try:
                subprocess.Popen([sys.executable, script_path])
            except Exception as e:
                CTkMessagebox(title="Error", message=f"Could not run script: {str(e)}")
    
    def open_project_folder(self):
        project_path = os.path.dirname(os.path.abspath(__file__))
        subprocess.Popen(f'explorer {project_path}')
    
    def clear_current_chat(self):
        if self.app.current_chat:
            self.app.current_chat['messages'] = []
            self.app.chat_text.configure(state="normal")
            self.app.chat_text.delete("1.0", "end")
            self.app.chat_text.configure(state="disabled")
            CTkMessagebox(title="Chat Cleared", message="Current chat has been cleared.")
    
    def export_chat(self):
        if self.app.current_chat:
            export_path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text Files", "*.txt")]
            )
            
            if export_path:
                with open(export_path, 'w', encoding='utf-8') as f:
                    for msg in self.app.current_chat['messages']:
                        f.write(f"{msg['role'].upper()}: {msg['content']}\n\n")
                CTkMessagebox(title="Export Successful", message=f"Chat exported to {export_path}")
    
    def show_chat_stats(self):
        if self.app.current_chat:
            messages = self.app.current_chat['messages']
            user_messages = [m for m in messages if m['role'] == 'user']
            ai_messages = [m for m in messages if m['role'] == 'assistant']
            
            stats_text = (
                f"Total Messages: {len(messages)}\n"
                f"User Messages: {len(user_messages)}\n"
                f"AI Responses: {len(ai_messages)}\n"
                f"Model: {self.app.current_chat.get('model', 'Unknown')}"
            )
            
            CTkMessagebox(title="Chat Statistics", message=stats_text)

# Optional: Main execution block
if __name__ == "__main__":
    root = ctk.CTk()
    app = OllamaChatApp(root)
    root.mainloop()
