import sys
import ollama
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                             QTextEdit, QLineEdit, QPushButton, QComboBox, QWidget, 
                             QFileDialog, QInputDialog, QLabel)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
import traceback
import json
import os

class OllamaChatThread(QThread):
    response_signal = pyqtSignal(str)

    def __init__(self, model, message):
        super().__init__()
        self.model = model
        self.message = message

    def run(self):
        try:
            response = ollama.chat(model=self.model, messages=[{
                'role': 'user', 
                'content': self.message
            }])  
            self.response_signal.emit(response['message']['content'])
        except Exception as e:
            self.response_signal.emit(f"Error: {str(e)}\n{traceback.format_exc()}")

class OllamaChatApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ollama Chat")
        self.setGeometry(100, 100, 600, 500)

        # Central widget and layout
        central_widget = QWidget()
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # Model selection
        model_layout = QHBoxLayout()
        self.model_combo = QComboBox()
        self.load_models()
        model_layout.addWidget(self.model_combo)
        main_layout.addLayout(model_layout)

        # Chat history
        self.chat_history = QTextEdit()
        self.chat_history.setReadOnly(True)
        main_layout.addWidget(self.chat_history)

        # Message input area
        input_layout = QHBoxLayout()
        self.message_input = QLineEdit()
        self.message_input.returnPressed.connect(self.send_message)
        
        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_message)
        
        self.clear_button = QPushButton("Clear Chat")
        self.clear_button.clicked.connect(self.clear_chat)

        self.save_button = QPushButton("Save Conversation")
        self.save_button.clicked.connect(self.save_conversation)

        input_layout.addWidget(self.message_input)
        input_layout.addWidget(self.send_button)
        input_layout.addWidget(self.clear_button)
        input_layout.addWidget(self.save_button)
        main_layout.addLayout(input_layout)

    def load_models(self):
        try:
            models = ollama.list()
            for model in models['models']:
                self.model_combo.addItem(model['name'])
        except Exception as e:
            self.chat_history.append(f"Error: {str(e)}\n{traceback.format_exc()}")

    def send_message(self):
        try:
            message = self.message_input.text().strip()
            if not message:
                return

            model = self.model_combo.currentText()
            self.chat_history.append(f"<b>You ({model}):</b> {message}")
            self.message_input.clear()

            # Start chat thread
            self.chat_thread = OllamaChatThread(model, message)
            self.chat_thread.response_signal.connect(self.display_response)
            self.chat_thread.start()
        except Exception as e:
            self.chat_history.append(f"Error: {str(e)}\n{traceback.format_exc()}")

    def display_response(self, response):
        try:
            self.chat_history.append(f"<b>AI:</b> {response}\n")
        except Exception as e:
            self.chat_history.append(f"Error: {str(e)}\n{traceback.format_exc()}")

    def clear_chat(self):
        try:
            self.chat_history.clear()
        except Exception as e:
            self.chat_history.append(f"Error: {str(e)}\n{traceback.format_exc()}")

    def save_conversation(self):
        try:
            filename, _ = QFileDialog.getSaveFileName(self, "Save Conversation", "", "JSON Files (*.json)")
            if filename:
                conversation = self.chat_history.toPlainText()
                with open(filename, "w") as file:
                    json.dump({"conversation": conversation}, file)
        except Exception as e:
            self.chat_history.append(f"Error: {str(e)}\n{traceback.format_exc()}")

def main():
    try:
        app = QApplication(sys.argv)
        chat_app = OllamaChatApp()
        chat_app.show()
        sys.exit(app.exec())
    except Exception as e:
        print(f"Error: {str(e)}\n{traceback.format_exc()}")

if __name__ == "__main__":
    main()
