import os
import customtkinter as ctk
import queue
import threading
import time

from chat_ui.utils.markdown_parser import MarkdownParser
from chat_ui.chat_manager.manager import ChatManager
from chat_ui.ui.message_display import MessageDisplay
from chat_ui.ui.input_handler import InputHandler
from chat_ui.ui.chat_list import ChatListManager

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
        self.root.geometry("1200x800")
        self.root.minsize(1000, 600)

        # Chat management
        self.chat_manager = ChatManager()
        self.current_chat = None
        self.response_queue = queue.Queue()

        # Initialize UI components
        self._setup_main_layout()
        self._setup_sidebar()
        self._setup_chat_area()
        self._setup_input_area()

        # Additional setup
        self.message_display = MessageDisplay(self.chat_text)
        self.input_handler = InputHandler(self)
        self.chat_list_manager = ChatListManager(self.chat_list, self.load_selected_chat)

        # Load existing chats
        self.load_existing_chats()

        # Start response processing thread
        self.response_thread = threading.Thread(target=self.process_responses, daemon=True)
        self.response_thread.start()

        # Schedule periodic queue checking
        self.root.after(100, self.check_response_queue)

        # Add animation tracking
        self.animation_running = False
        self.animation_thread = None

    def _setup_main_layout(self):
        # Main grid layout
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        # Main frame
        self.main_frame = ctk.CTkFrame(self.root, corner_radius=10)
        self.main_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=4)
        self.main_frame.grid_rowconfigure(0, weight=1)

    def _setup_sidebar(self):
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

    def _setup_chat_area(self):
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
            text_color="black",
            fg_color=("#f0f0f0", "#2c2c2c")
        )
        self.chat_text.grid(row=0, column=0, sticky="nsew")
        
        # Configure scrollbar
        self.chat_text_scrollbar.configure(command=self.chat_text.yview)

        # Configure text tags for styling
        self.chat_text.tag_config("user_tag", foreground="light blue")
        self.chat_text.tag_config("ai_tag", foreground="light green")
        self.chat_text.tag_config("typing_tag", foreground="gray")

    def _setup_input_area(self):
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
            hover_color=("blue3", "blue4")
        )
        self.send_button.grid(row=0, column=1, padx=5, pady=5)

    def load_existing_chats(self):
        """
        Load and display existing chat sessions
        """
        # Get list of chats from chat manager
        existing_chats = self.chat_manager.list_chats()
        
        # Update chat list in sidebar
        self.chat_list_manager.load_existing_chats(existing_chats)
        
        # If no chats exist, show welcome message
        if not existing_chats:
            self.show_welcome_message()

    def clear_all_chats(self):
        response = ConfirmationDialog.show(
            title="Confirm Clear", 
            message="Are you sure you want to clear all chats?"
        )
        
        if response == "Yes":
            self.chat_manager.clear_all_chats()
            self.load_existing_chats()
            self.current_chat = None
            self.message_display.clear_chat()

    def populate_models(self):
        try:
            models = OllamaModelHandler.get_available_models()
            
            if models:
                self.model_combo.configure(values=models)
                self.model_combo.set(models[0])
            else:
                self.model_combo.configure(values=["No models found"])
                self.model_combo.set("No models found")
        except Exception as e:
            print(f"Error populating models: {e}")
            self.model_combo.configure(values=["Error loading models"])
            self.model_combo.set("Error loading models")

    def create_new_chat(self):
        """
        Create a new chat session
        """
        # Utiliser cget pour récupérer les valeurs du modèle
        model = self.model_combo.get()
        if model in ["No models found", "Error loading models"]:
            model = 'default'
        
        # Create a new chat
        new_chat = self.chat_manager.create_new_chat(model)
        
        # Update the UI
        self.current_chat = new_chat
        self.load_existing_chats()  # Refresh the chat list
        self.load_selected_chat(new_chat)  # Load the new chat
        
        # Clear previous messages
        self.message_display.clear_chat()
        
        return new_chat

    def load_selected_chat(self, chat):
        self.current_chat = chat
        self.message_display.load_chat_messages(chat)
        
        # Vérifier si le modèle existe dans les valeurs disponibles
        model = chat.get('model')
        if model and model in self.model_combo.cget("values").split():
            self.model_combo.set(model)

    def send_message(self, event=None):
        if not self.current_chat:
            # Utiliser cget pour récupérer les valeurs du modèle
            model = self.model_combo.get() if self.model_combo.get() not in ["No models found", "Error loading models"] else 'default'
            self.current_chat = self.chat_manager.create_new_chat(model)
            self.load_existing_chats()

        message = self.message_entry.get().strip()
        if not message:
            return

        self.input_handler.send_message(message)

    def process_responses(self):
        while True:
            try:
                model, response, think_content, is_complete = self.response_queue.get()
                
                self.current_chat = self.chat_manager.add_message(
                    self.current_chat, 'assistant', response
                )
                
                self.chat_manager.save_chat(self.current_chat)
                
                self.root.after(0, self.handle_ai_response, response, think_content)
                
                self.response_queue.task_done()
            except Exception as e:
                print(f"Error processing response: {e}")

    def handle_ai_response(self, response, think_content):
        self.input_handler.handle_ai_response(response, think_content)

    def check_response_queue(self):
        try:
            model, response, think_content, is_complete = self.response_queue.get_nowait()
            self.root.after(0, self.handle_ai_response, response, think_content)
        except queue.Empty:
            pass
        
        self.root.after(100, self.check_response_queue)

    def show_welcome_message(self):
        self.message_display.show_welcome_message()
