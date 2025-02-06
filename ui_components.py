import customtkinter as ctk
from CTkMessagebox import CTkMessagebox

class ChatListItem(ctk.CTkFrame):
    """A custom widget for displaying chat list items"""
    def __init__(self, master, chat, on_click_callback, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.chat = chat
        self.on_click_callback = on_click_callback

        # Chat title with truncation
        title = chat.get('title', 'Untitled Chat')
        if len(title) > 25:
            title = title[:25] + '...'
        
        self.chat_title = ctk.CTkLabel(
            self, 
            text=title, 
            anchor="w",
            font=ctk.CTkFont(size=12)
        )
        self.chat_title.pack(side="left", expand=True, fill="x")
        
        # Model badge
        self.model_badge = ctk.CTkLabel(
            self, 
            text=chat.get('model', 'Unknown'),
            fg_color="gray",
            text_color="white",
            corner_radius=10,
            width=60,
            height=20,
            font=ctk.CTkFont(size=10)
        )
        self.model_badge.pack(side="right", padx=5)
        
        # Bind click events
        self.bind("<Button-1>", self._on_click)
        self.chat_title.bind("<Button-1>", self._on_click)
        self.model_badge.bind("<Button-1>", self._on_click)

    def _on_click(self, event):
        """Handle click event and call the callback"""
        self.on_click_callback(self.chat)

class ConfirmationDialog:
    """A utility class for creating confirmation dialogs"""
    @staticmethod
    def show(title, message, icon="warning", options=("Yes", "No")):
        """
        Show a confirmation dialog
        
        Args:
            title (str): Dialog title
            message (str): Dialog message
            icon (str, optional): Dialog icon. Defaults to "warning".
            options (tuple, optional): Dialog options. Defaults to ("Yes", "No").
        
        Returns:
            str: Selected option
        """
        confirm = CTkMessagebox(
            title=title, 
            message=message,
            icon=icon, 
            option_1=options[0], 
            option_2=options[1]
        )
        return confirm.get()

class MessageBox:
    """A utility class for showing message boxes"""
    @staticmethod
    def show(title, message, icon="info"):
        """
        Show a message box
        
        Args:
            title (str): Dialog title
            message (str): Dialog message
            icon (str, optional): Dialog icon. Defaults to "info".
        """
        CTkMessagebox(
            title=title, 
            message=message, 
            icon=icon
        )
