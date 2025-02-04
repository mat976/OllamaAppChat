import sys
from PyQt6.QtWidgets import QApplication
from chat_ui import OllamaChatApp

def main():
    app = QApplication(sys.argv)
    chat_app = OllamaChatApp()
    chat_app.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
