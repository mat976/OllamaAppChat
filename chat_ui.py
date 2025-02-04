import os
import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
import queue
import threading

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
        self.root.geometry("1400x800")
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
        self.main_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=4)
        self.main_frame.grid_rowconfigure(0, weight=1)

        # Sidebar for chat list
        self.sidebar_frame = ctk.CTkFrame(self.main_frame, width=250, corner_radius=10)
        self.sidebar_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(2, weight=1)

        # Sidebar title
        self.sidebar_title = ctk.CTkLabel(
            self.sidebar_frame, 
            text="🤖 Ollama Chats", 
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.sidebar_title.grid(row=0, column=0, padx=20, pady=(20, 10))

        # New Chat Button
        self.new_chat_button = ctk.CTkButton(
            self.sidebar_frame, 
            text="+ New Chat", 
            command=self.create_new_chat,
            corner_radius=20
        )
        self.new_chat_button.grid(row=1, column=0, padx=20, pady=10)

        # Chat List
        self.chat_list = ctk.CTkScrollableFrame(
            self.sidebar_frame, 
            corner_radius=10
        )
        self.chat_list.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")

        # Chat Area
        self.chat_frame = ctk.CTkFrame(self.main_frame, corner_radius=10)
        self.chat_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.chat_frame.grid_rowconfigure(0, weight=1)
        self.chat_frame.grid_columnconfigure(0, weight=1)

        # Chat Text Area
        self.chat_text = ctk.CTkTextbox(
            self.chat_frame, 
            state="disabled", 
            font=ctk.CTkFont(size=14),
            corner_radius=10
        )
        self.chat_text.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # Model Selection
        self.model_frame = ctk.CTkFrame(self.chat_frame, fg_color="transparent")
        self.model_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        self.model_frame.grid_columnconfigure(0, weight=1)

        self.model_combo = ctk.CTkComboBox(
            self.model_frame, 
            state="readonly", 
            width=300
        )
        self.model_combo.grid(row=0, column=0, padx=(0, 10), pady=10, sticky="ew")

        # Message Input Frame
        self.input_frame = ctk.CTkFrame(self.chat_frame, fg_color="transparent")
        self.input_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        self.input_frame.grid_columnconfigure(0, weight=1)

        # Message Entry
        self.message_entry = ctk.CTkEntry(
            self.input_frame, 
            placeholder_text="Type your message...", 
            height=40,
            corner_radius=20
        )
        self.message_entry.grid(row=0, column=0, padx=(0, 10), pady=10, sticky="ew")
        self.message_entry.bind('<Return>', self.send_message)

        # Send Button
        self.send_button = ctk.CTkButton(
            self.input_frame, 
            text="Send", 
            command=self.send_message,
            width=100,
            corner_radius=20
        )
        self.send_button.grid(row=0, column=1, padx=10, pady=10)

        # Populate models
        self.populate_models()
        
        # Load existing chats
        self.load_existing_chats()

        # Start response processing thread
        self.response_thread = threading.Thread(target=self.process_responses, daemon=True)
        self.response_thread.start()

        # Schedule periodic queue checking
        self.root.after(100, self.check_response_queue)

    def populate_models(self):
        """Populate model dropdown with available Ollama models"""
        models = OllamaModelHandler.get_available_models()
        if models:
            self.model_combo.configure(values=models)
            self.model_combo.set(models[0])
        else:
            CTkMessagebox(
                title="Error", 
                message="No Ollama models found. Please install models first.", 
                icon="cancel"
            )

    def create_new_chat(self):
        """Create a new chat session"""
        model = self.model_combo.get()
        new_chat = self.chat_manager.create_new_chat(model)
        
        # Create a button for the new chat
        chat_button = ctk.CTkButton(
            self.chat_list, 
            text=f"Chat {new_chat['id'][:8]}",
            command=lambda chat=new_chat: self.load_chat(chat),
            corner_radius=10
        )
        chat_button.pack(pady=5, fill='x')

        # Load the new chat
        self.load_chat(new_chat)

    def load_chat(self, chat):
        """Load an existing chat session"""
        self.current_chat = chat
        
        # Clear previous chat text
        self.chat_text.configure(state="normal")
        self.chat_text.delete("1.0", "end")
        
        # Display chat history
        for msg in chat.get('messages', []):
            role = msg['role']
            content = msg['content']
            self.display_message(role, content)
        
        # Disable text box
        self.chat_text.configure(state="disabled")
        self.chat_text.see("end")

    def load_existing_chats(self):
        """Load existing chat sessions from file"""
        chats = self.chat_manager.list_chats()
        for chat in chats:
            chat_button = ctk.CTkButton(
                self.chat_list, 
                text=f"Chat {chat['id'][:8]}",
                command=lambda c=chat: self.load_chat(c),
                corner_radius=10
            )
            chat_button.pack(pady=5, fill='x')

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

    def display_message(self, role, content):
        """Display a message in the chat text area"""
        self.chat_text.configure(state="normal")
        
        # Determine formatting based on role
        if role == 'user':
            self.chat_text.insert("end", f"You: {content}\n\n")
        else:
            self.chat_text.insert("end", f"AI: {content}\n\n")
        
        self.chat_text.configure(state="disabled")
        self.chat_text.see("end")

    def process_responses(self):
        """Process responses from the model in a separate thread"""
        while True:
            try:
                # Unpack the response with the completion flag
                model, response, is_complete = self.response_queue.get()
                
                # Add AI response to current chat
                self.current_chat = self.chat_manager.add_message(
                    self.current_chat, 'assistant', response
                )
                
                # Save the chat
                self.chat_manager.save_chat(self.current_chat)
                
                # Display response in main thread
                self.root.after(0, self.display_message, 'assistant', response)
                
                self.response_queue.task_done()
            except Exception as e:
                print(f"Error processing response: {e}")

    def check_response_queue(self):
        """Check response queue periodically"""
        try:
            # Non-blocking check of the queue
            model, response, is_complete = self.response_queue.get_nowait()
            self.root.after(0, self.display_message, 'assistant', response)
        except queue.Empty:
            pass
        
        # Schedule next check
        self.root.after(100, self.check_response_queue)

# Optional: Main execution block
if __name__ == "__main__":
    root = ctk.CTk()
    app = OllamaChatApp(root)
    root.mainloop()
