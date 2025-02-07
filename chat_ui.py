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
from ui_components import ChatListItem, ConfirmationDialog, MessageBox

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

        # Chat List
        self.chat_list = ctk.CTkScrollableFrame(
            self.sidebar_frame, 
            corner_radius=10,
            height=500,
            width=230
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
            yscrollcommand=self.chat_text_scrollbar.set,
            font=ctk.CTkFont(size=14),
            text_color="white",
            fg_color=("#f0f0f0", "#2c2c2c")
        )
        self.chat_text.grid(row=0, column=0, sticky="nsew")
        
        # Configure scrollbar
        self.chat_text_scrollbar.configure(command=self.chat_text.yview)

        # Configure text tags for styling
        self.chat_text.tag_config("user_tag", foreground="light blue")
        self.chat_text.tag_config("ai_tag", foreground="light green")
        self.chat_text.tag_config("typing_tag", foreground="gray")

        # Model Selection Frame
        self.model_frame = ctk.CTkFrame(self.chat_frame, fg_color="transparent")
        self.model_frame.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        self.model_frame.grid_columnconfigure(0, weight=1)

        # Model Selection Combo Box
        self.model_combo = ctk.CTkComboBox(
            self.model_frame, 
            state="readonly", 
            width=250
        )
        self.model_combo.grid(row=0, column=0, padx=(0, 5), pady=5, sticky="ew")

        # Populate models
        self.populate_models()

        # Message Input Frame
        self.input_frame = ctk.CTkFrame(self.chat_frame, fg_color="transparent")
        self.input_frame.grid(row=2, column=0, padx=5, pady=5, sticky="ew")
        self.input_frame.grid_columnconfigure(0, weight=1)

        # Message Entry with improved styling
        self.message_entry = ctk.CTkEntry(
            self.input_frame, 
            placeholder_text="Type your message...",
            width=600,
            height=40,
            font=ctk.CTkFont(size=14),
            corner_radius=20,
            border_width=2,
            border_color=("gray70", "gray30")
        )
        self.message_entry.grid(row=0, column=0, padx=(0, 10), pady=5, sticky="ew")
        self.message_entry.bind("<Return>", self.send_message)

        # Send Button with improved styling
        self.send_button = ctk.CTkButton(
            self.input_frame, 
            text="Send", 
            command=self.send_message,
            width=100,
            height=40,
            corner_radius=20,
            font=ctk.CTkFont(size=14, weight="bold"),
            hover_color=("blue3", "blue4")
        )
        self.send_button.grid(row=0, column=1, padx=5, pady=5)

        # Load existing chats
        self.load_existing_chats()

        # Start response processing thread
        self.response_thread = threading.Thread(target=self.process_responses, daemon=True)
        self.response_thread.start()

        # Schedule periodic queue checking
        self.root.after(100, self.check_response_queue)

        # Show welcome message if no chats exist
        if not self.chat_list.winfo_children():
            self.show_welcome_message()

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
            chat_item = ChatListItem(
                self.chat_list, 
                chat, 
                on_click_callback=self.load_selected_chat
            )
            chat_item.pack(fill="x", padx=5, pady=3)

    def clear_all_chats(self):
        """Clear all existing chats with confirmation"""
        # Use confirmation dialog from ui_components
        response = ConfirmationDialog.show(
            title="Confirm Clear", 
            message="Are you sure you want to clear all chats?"
        )
        
        if response == "Yes":
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
            MessageBox.show(
                title="Error", 
                message="No chat selected to delete.", 
                icon="cancel"
            )
            return

        # Create a confirmation dialog
        response = ConfirmationDialog.show(
            title="Confirm Delete Chat", 
            message=f"Are you sure you want to delete this chat: {self.current_chat.get('title', 'Untitled Chat')}?"
        )
        
        if response == "Delete":
            # Delete the current chat
            self.chat_manager.delete_chat(self.current_chat['id'])
            
            # Refresh chat list
            self.load_existing_chats()
            
            # Reset current chat
            self.current_chat = None
            
            # Clear chat text
            self.chat_text.configure(state="normal")
            self.chat_text.delete("1.0", "end")
            self.chat_text.configure(state="disabled")
            
            # Show confirmation
            MessageBox.show(
                title="Chat Deleted", 
                message="The chat session has been deleted."
            )

    def get_last_response(self):
        """Get the last AI response from the current chat"""
        if self.current_chat and self.current_chat.get('messages'):
            last_message = self.current_chat['messages'][-1]
            return last_message['content'] if last_message['role'] == 'assistant' else None
        return None

    def export_chat_to_file(self, file_path):
        """Export the current chat to a file"""
        if self.current_chat:
            with open(file_path, 'w', encoding='utf-8') as f:
                for msg in self.current_chat.get('messages', []):
                    f.write(f"{msg['role'].upper()}: {msg['content']}\n\n")

    def get_chat_statistics(self):
        """Get chat statistics"""
        if not self.current_chat:
            return {}
        
        messages = self.current_chat.get('messages', [])
        user_messages = [m for m in messages if m['role'] == 'user']
        ai_messages = [m for m in messages if m['role'] == 'assistant']
        
        return {
            'total_messages': len(messages),
            'user_messages': len(user_messages),
            'ai_messages': len(ai_messages),
            'model': self.current_chat.get('model', 'Unknown')
        }

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

    def send_message(self, event=None):
        """Send a message in the current chat"""
        # If no current chat exists, automatically create a new chat
        if not self.current_chat:
            # Use the first available model or default to 'default'
            model = self.model_combo.get() if self.model_combo.get() != "No models found" else 'default'
            self.current_chat = self.chat_manager.create_new_chat(model)
            
            # Refresh chat list to show the new chat
            self.load_existing_chats()

        message = self.message_entry.get().strip()
        if not message:
            return

        # Clear input
        self.message_entry.delete(0, 'end')

        # Disable input during processing
        self.message_entry.configure(state='disabled')
        self.send_button.configure(state='disabled')

        # Expand chat text area to make room for typing indicator
        self.chat_text_frame.grid_rowconfigure(0, weight=10)

        # Show typing indicator
        self.display_typing_indicator()

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

    def display_typing_indicator(self):
        """Display a typing indicator while waiting for AI response"""
        self.chat_text.configure(state="normal")
        
        # Insert typing indicator with more visual appeal
        typing_tag = "typing_indicator"
        self.chat_text.tag_config(typing_tag, 
            foreground="gray",
            spacing1=10,  # Space above the text
            spacing3=10   # Space below the text
        )
        
        # Animated thinking indicator
        thinking_dots = "🤖 Thinking"
        self.chat_text.insert("end", f"\n{thinking_dots}", typing_tag)
        
        # Animate dots
        def animate_dots(count=0):
            if hasattr(self, 'typing_job'):
                # Remove previous dots
                self.chat_text.configure(state="normal")
                last_line = self.chat_text.get("end-2l", "end-1l")
                if thinking_dots in last_line:
                    # Update dots
                    dots = "." * ((count % 3) + 1)
                    self.chat_text.delete("end-2l", "end")
                    self.chat_text.insert("end", f"\n{thinking_dots}{dots}", typing_tag)
                    self.chat_text.configure(state="disabled")
                    self.chat_text.see("end")
                
                # Schedule next animation
                self.typing_job = self.root.after(500, animate_dots, (count + 1) % 4)
        
        # Start dot animation
        self.typing_job = self.root.after(500, animate_dots)
        
        self.chat_text.configure(state="disabled")
        self.chat_text.see("end")

    def handle_ai_response(self, response, think_content):
        """
        Handle AI response with improved display and interaction
        
        Args:
            response (str): AI's response message
            think_content (str, optional): Internal thought content
        """
        # Cancel typing animation
        if hasattr(self, 'typing_job'):
            self.root.after_cancel(self.typing_job)
        
        # Remove typing indicator
        self.chat_text.configure(state="normal")
        last_line = self.chat_text.get("end-2l", "end-1l")
        if "🤖 Thinking" in last_line:
            self.chat_text.delete("end-2l", "end")
        
        # Restore original text area weight
        self.chat_text_frame.grid_rowconfigure(0, weight=1)
        
        # Display AI message
        self.display_message('assistant', response, think_content)
        
        # Re-enable input
        self.message_entry.configure(state='normal')
        self.send_button.configure(state='normal')
        
        # Focus back on message entry
        self.message_entry.focus_set()

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
                self.root.after(0, self.handle_ai_response, response, think_content)
                
                self.response_queue.task_done()
            except Exception as e:
                print(f"Error processing response: {e}")

    def check_response_queue(self):
        """Check response queue periodically"""
        try:
            # Non-blocking check of the queue
            model, response, think_content, is_complete = self.response_queue.get_nowait()
            self.root.after(0, self.handle_ai_response, response, think_content)
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

    def create_chat_interface(self, chat):
        """Create the chat interface for a specific chat"""
        # Clear any existing chat frame contents
        for widget in self.chat_frame.winfo_children():
            widget.destroy()

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
            yscrollcommand=self.chat_text_scrollbar.set,
            font=ctk.CTkFont(size=14),  # Increased font size
            text_color="white",  # Ensure readability
            fg_color=("#f0f0f0", "#2c2c2c")  # Light background in light mode, dark in dark mode
        )
        self.chat_text.grid(row=0, column=0, sticky="nsew")
        
        # Configure scrollbar
        self.chat_text_scrollbar.configure(command=self.chat_text.yview)

        # Configure text tags for styling
        self.chat_text.tag_config("user_tag", foreground="light blue")
        self.chat_text.tag_config("ai_tag", foreground="light green")
        self.chat_text.tag_config("typing_tag", foreground="gray")

        # Model Selection Frame
        self.model_frame = ctk.CTkFrame(self.chat_frame, fg_color="transparent")
        self.model_frame.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        self.model_frame.grid_columnconfigure(0, weight=1)

        # Model Selection Combo Box
        self.model_combo = ctk.CTkComboBox(
            self.model_frame, 
            state="readonly", 
            width=250
        )
        self.model_combo.grid(row=0, column=0, padx=(0, 5), pady=5, sticky="ew")
        self.model_combo.configure(values=[chat['model']])
        self.model_combo.set(chat['model'])

        # Message Input Frame
        self.input_frame = ctk.CTkFrame(self.chat_frame, fg_color="transparent")
        self.input_frame.grid(row=2, column=0, padx=5, pady=5, sticky="ew")
        self.input_frame.grid_columnconfigure(0, weight=1)

        # Message Entry with improved styling
        self.message_entry = ctk.CTkEntry(
            self.input_frame, 
            placeholder_text="Type your message...",
            width=600,
            height=40,
            font=ctk.CTkFont(size=14),
            corner_radius=20,
            border_width=2,
            border_color=("gray70", "gray30")
        )
        self.message_entry.grid(row=0, column=0, padx=(0, 10), pady=5, sticky="ew")
        self.message_entry.bind("<Return>", self.send_message)

        # Send Button with improved styling
        self.send_button = ctk.CTkButton(
            self.input_frame, 
            text="Send", 
            command=self.send_message,
            width=100,
            height=40,
            corner_radius=20,
            font=ctk.CTkFont(size=14, weight="bold"),
            hover_color=("blue3", "blue4")
        )
        self.send_button.grid(row=0, column=1, padx=5, pady=5)

        # Set current chat
        self.current_chat = chat

        # Start response processing thread
        self.response_queue = queue.Queue()
        self.response_thread = threading.Thread(target=self.process_responses, daemon=True)
        self.response_thread.start()

        # Schedule periodic queue checking
        self.root.after(100, self.check_response_queue)

        # Load chat messages
        self.load_chat_messages(chat)

        # Focus on message entry
        self.message_entry.focus_set()

    def load_chat_messages(self, chat):
        """
        Load chat messages for the given chat
        """
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

    def show_welcome_message(self):
        """Show a welcome message if no chats exist"""
        self.chat_text.configure(state="normal")
        self.chat_text.insert("1.0", "Welcome to Ollama AI Chat! 🤖\n\n")
        self.chat_text.insert("end", "To get started, click the + New Chat button to create a new chat session.\n\n")
        self.chat_text.insert("end", "You can also load existing chats from the sidebar.\n\n")
        self.chat_text.configure(state="disabled")

if __name__ == "__main__":
    root = ctk.CTk()
    app = OllamaChatApp(root)
    root.mainloop()
