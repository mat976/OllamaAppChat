import customtkinter as ctk
from chat_ui import OllamaChatApp

def main():
    """
    Main entry point for the Ollama Chat Application
    """
    # Configure CustomTkinter
    ctk.set_appearance_mode("dark")  # Modes: system (default), light, dark
    ctk.set_default_color_theme("blue")  # Themes: blue (default), dark-blue, green

    # Create the main application window
    root = ctk.CTk()
    app = OllamaChatApp(root)
    
    # Start the application main loop
    root.mainloop()

if __name__ == "__main__":
    main()
