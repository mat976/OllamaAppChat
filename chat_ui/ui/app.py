import os
import customtkinter as ctk
import queue
import threading
import time
from tkinter import filedialog

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

        # List to store attached file paths
        self.attached_files = []

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

        # Attach File Button
        self.attach_button = ctk.CTkButton(
            self.input_frame, 
            text="📎", 
            command=self.attach_file,
            width=50,
            height=40,
            corner_radius=20,
            fg_color=("gray75", "gray30"),
            hover_color=("gray70", "gray25")
        )
        self.attach_button.grid(row=0, column=2, padx=5, pady=5)

        # Listbox to display attached files
        self.files_listbox = ctk.CTkScrollableFrame(
            self.input_frame,
            width=200,
            height=100
        )
        self.files_listbox.grid(row=1, column=0, columnspan=3, padx=5, pady=5, sticky="ew")

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
        self.send_button.grid(row=0, column=3, padx=5, pady=5)

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
        """
        Populate the model selection dropdown with available models
        """
        try:
            # Récupérer les modèles disponibles
            models = OllamaModelHandler.get_available_models()
            
            # Gérer les différents cas de modèles
            if models:
                # Configurer les modèles disponibles
                self.model_combo.configure(values=models)
                self.model_combo.set(models[0])  # Sélectionner le premier modèle par défaut
            else:
                # Aucun modèle trouvé
                default_options = ["No models found", "default"]
                self.model_combo.configure(values=default_options)
                self.model_combo.set(default_options[0])
        
        except Exception as e:
            # Gérer les erreurs de chargement des modèles
            error_options = ["Error loading models", "default"]
            print(f"Error populating models: {e}")
            self.model_combo.configure(values=error_options)
            self.model_combo.set(error_options[0])

    def create_new_chat(self):
        """
        Create a new chat session
        """
        # Récupérer le modèle sélectionné
        model = self.model_combo.get()
        
        # Utiliser un modèle par défaut si nécessaire
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

    def send_message(self, event=None):
        if not self.current_chat:
            # Récupérer le modèle sélectionné
            model = self.model_combo.get()
            
            # Utiliser un modèle par défaut si nécessaire
            if model in ["No models found", "Error loading models"]:
                model = 'default'
            
            # Créer un nouveau chat
            self.current_chat = self.chat_manager.create_new_chat(model)
            self.load_existing_chats()

        message = self.message_entry.get().strip()
        if not message and not self.attached_files:
            return

        # Prepare the message data
        message_data = {
            "text": message,
            "files": self.attached_files.copy()  # Send a copy of the list
        }

        # Send the message using the input handler
        self.input_handler.send_message(message_data)

        # Clear the message entry and attached files after sending
        self.message_entry.delete(0, ctk.END)
        
        # Clear the attached files list and its display
        self.attached_files.clear()
        for widget in self.files_listbox.winfo_children():
            widget.destroy()

    def load_selected_chat(self, chat):
        self.current_chat = chat
        self.message_display.load_chat_messages(chat)
        
        # Vérifier si le modèle existe dans les valeurs disponibles
        model = chat.get('model')
        available_models = self.model_combo.cget("values")
        
        # Vérifier si le modèle existe dans la liste des modèles disponibles
        if model and model in available_models:
            self.model_combo.set(model)

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

    def attach_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            # Check if file is already attached
            if file_path not in self.attached_files:
                self.attached_files.append(file_path)
                
                # Create a frame for each attached file
                file_frame = ctk.CTkFrame(self.files_listbox, fg_color="transparent")
                file_frame.pack(fill="x", padx=5, pady=2)
                
                # File name label
                file_label = ctk.CTkLabel(
                    file_frame, 
                    text=os.path.basename(file_path), 
                    anchor="w"
                )
                file_label.pack(side="left", expand=True, fill="x")
                
                # Remove file button
                remove_button = ctk.CTkButton(
                    file_frame, 
                    text="✖", 
                    width=30, 
                    height=20, 
                    fg_color="red", 
                    hover_color="darkred",
                    command=lambda path=file_path: self.remove_attached_file(path)
                )
                remove_button.pack(side="right", padx=5)

    def remove_attached_file(self, file_path):
        if file_path in self.attached_files:
            self.attached_files.remove(file_path)
            # Refresh the files listbox
            for widget in self.files_listbox.winfo_children():
                widget.destroy()
            
            # Recreate the file list
            for path in self.attached_files:
                file_frame = ctk.CTkFrame(self.files_listbox, fg_color="transparent")
                file_frame.pack(fill="x", padx=5, pady=2)
                
                file_label = ctk.CTkLabel(
                    file_frame, 
                    text=os.path.basename(path), 
                    anchor="w"
                )
                file_label.pack(side="left", expand=True, fill="x")
                
                remove_button = ctk.CTkButton(
                    file_frame, 
                    text="✖", 
                    width=30, 
                    height=20, 
                    fg_color="red", 
                    hover_color="darkred",
                    command=lambda p=path: self.remove_attached_file(p)
                )
                remove_button.pack(side="right", padx=5)
