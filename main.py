import customtkinter as ctk
from chat_ui.ui.app import OllamaChatApp

def main():
    """
    Main entry point for the Ollama Chat Application
    """
    # Configure CustomTkinter global settings
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    # Create the main Tkinter root window
    root = ctk.CTk()
    root.title("🤖 Ollama AI Chat")
    root.geometry("1200x800")
    root.minsize(1000, 600)

    # Initialize the chat application
    app = OllamaChatApp(root)

    # Start the main event loop
    root.mainloop()

if __name__ == "__main__":
    main()
