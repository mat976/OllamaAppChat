import customtkinter as ctk
from ui_components import ChatListItem

class ChatListManager:
    def __init__(self, chat_list_frame, load_selected_chat_callback):
        """
        Initialize the chat list manager
        
        Args:
            chat_list_frame (ctk.CTkScrollableFrame): Frame to display chat list
            load_selected_chat_callback (callable): Callback to load a selected chat
        """
        self.chat_list_frame = chat_list_frame
        self.load_selected_chat_callback = load_selected_chat_callback

    def load_existing_chats(self, chats):
        """
        Load and display existing chats in the sidebar
        
        Args:
            chats (list): List of chat sessions
        """
        # Clear existing chat list
        for widget in self.chat_list_frame.winfo_children():
            widget.destroy()
        
        if not chats:
            # Show a placeholder when no chats exist
            no_chats_label = ctk.CTkLabel(
                self.chat_list_frame, 
                text="No chats yet. Start a new chat!",
                text_color="gray"
            )
            no_chats_label.pack(pady=20)
            return
        
        # Create a compact and visually appealing chat list
        for chat in chats:
            chat_item = ChatListItem(
                self.chat_list_frame, 
                chat, 
                on_click_callback=self.load_selected_chat_callback
            )
            chat_item.pack(fill="x", padx=5, pady=3)

    def add_chat_to_list(self, chat):
        """
        Add a new chat to the list
        
        Args:
            chat (dict): Chat session to add
        """
        # Remove the "No chats" placeholder if it exists
        for widget in self.chat_list_frame.winfo_children():
            if isinstance(widget, ctk.CTkLabel) and widget.cget("text") == "No chats yet. Start a new chat!":
                widget.destroy()
        
        # Create and add the new chat item
        chat_item = ChatListItem(
            self.chat_list_frame, 
            chat, 
            on_click_callback=self.load_selected_chat_callback
        )
        chat_item.pack(fill="x", padx=5, pady=3, side="top")

    def remove_chat_from_list(self, chat_id):
        """
        Remove a chat from the list
        
        Args:
            chat_id (str): ID of the chat to remove
        """
        for widget in self.chat_list_frame.winfo_children():
            if hasattr(widget, 'chat') and widget.chat['id'] == chat_id:
                widget.destroy()
                break
        
        # If no chats remain, show the placeholder
        if not self.chat_list_frame.winfo_children():
            no_chats_label = ctk.CTkLabel(
                self.chat_list_frame, 
                text="No chats yet. Start a new chat!",
                text_color="gray"
            )
            no_chats_label.pack(pady=20)
