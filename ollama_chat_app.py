import sys
import ollama
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                             QTextEdit, QLineEdit, QPushButton, QComboBox, QWidget, 
                             QLabel, QStackedWidget, QSplitter)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
import traceback

class ModelChatThread(QThread):
    response_signal = pyqtSignal(str, str)

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
            self.response_signal.emit(
                self.model, 
                response['message']['content']
            )
        except Exception as e:
            self.response_signal.emit(
                self.model, 
                f"Error: {str(e)}\n{traceback.format_exc()}"
            )

class OllamaChatApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ollama Chat")
        self.setGeometry(100, 100, 1000, 700)

        # Central widget and main layout
        central_widget = QWidget()
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # Mode toggle button
        self.mode_toggle_button = QPushButton("Switch to Dual AI Mode")
        self.mode_toggle_button.clicked.connect(self.toggle_mode)
        main_layout.addWidget(self.mode_toggle_button)

        # Stacked widget to hold different modes
        self.mode_stack = QStackedWidget()
        main_layout.addWidget(self.mode_stack)

        # Create Solo Mode Widget
        self.solo_mode_widget = QWidget()
        solo_mode_layout = QVBoxLayout()
        self.solo_mode_widget.setLayout(solo_mode_layout)

        # Solo Mode Model Selection
        solo_model_layout = QHBoxLayout()
        self.solo_model_combo = QComboBox()
        solo_model_layout.addWidget(QLabel("Model:"))
        solo_model_layout.addWidget(self.solo_model_combo)
        solo_mode_layout.addLayout(solo_model_layout)

        # Solo Mode Chat History
        self.solo_chat_history = QTextEdit()
        self.solo_chat_history.setReadOnly(True)
        solo_mode_layout.addWidget(self.solo_chat_history)

        # Solo Mode Input Area
        solo_input_layout = QHBoxLayout()
        self.solo_message_input = QLineEdit()
        self.solo_message_input.setPlaceholderText("Enter your message...")
        self.solo_message_input.returnPressed.connect(lambda: self.send_message(mode='solo'))
        solo_input_layout.addWidget(self.solo_message_input)

        self.solo_send_button = QPushButton("Send")
        self.solo_send_button.clicked.connect(lambda: self.send_message(mode='solo'))
        solo_input_layout.addWidget(self.solo_send_button)
        solo_mode_layout.addLayout(solo_input_layout)

        # Create Dual Mode Widget
        self.dual_mode_widget = QWidget()
        dual_mode_layout = QVBoxLayout()
        self.dual_mode_widget.setLayout(dual_mode_layout)

        # Dual Mode Model Selection
        dual_model_layout = QHBoxLayout()
        self.dual_model1_combo = QComboBox()
        self.dual_model2_combo = QComboBox()
        dual_model_layout.addWidget(QLabel("Model 1:"))
        dual_model_layout.addWidget(self.dual_model1_combo)
        dual_model_layout.addWidget(QLabel("Model 2:"))
        dual_model_layout.addWidget(self.dual_model2_combo)
        dual_mode_layout.addLayout(dual_model_layout)

        # Dual Mode Chat Splitter
        self.dual_chat_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.dual_chat_history1 = QTextEdit()
        self.dual_chat_history2 = QTextEdit()
        self.dual_chat_history1.setReadOnly(True)
        self.dual_chat_history2.setReadOnly(True)
        self.dual_chat_splitter.addWidget(self.dual_chat_history1)
        self.dual_chat_splitter.addWidget(self.dual_chat_history2)
        dual_mode_layout.addWidget(self.dual_chat_splitter)

        # Dual Mode Input Area
        dual_input_layout = QHBoxLayout()
        self.dual_message_input = QLineEdit()
        self.dual_message_input.setPlaceholderText("Enter your message...")
        self.dual_message_input.returnPressed.connect(lambda: self.send_message(mode='dual'))
        dual_input_layout.addWidget(self.dual_message_input)

        self.dual_send_button = QPushButton("Compare Responses")
        self.dual_send_button.clicked.connect(lambda: self.send_message(mode='dual'))
        dual_input_layout.addWidget(self.dual_send_button)
        dual_mode_layout.addLayout(dual_input_layout)

        # Add widgets to stacked widget
        self.mode_stack.addWidget(self.solo_mode_widget)
        self.mode_stack.addWidget(self.dual_mode_widget)

        # Load models
        self.load_models()

        # Start in solo mode
        self.current_mode = 'solo'
        self.mode_stack.setCurrentWidget(self.solo_mode_widget)

    def load_models(self):
        try:
            models = ollama.list()
            available_models = [model['name'] for model in models['models']]
            
            # Populate solo mode model combo
            self.solo_model_combo.clear()
            self.solo_model_combo.addItems(available_models)
            
            # Populate dual mode model combos
            self.dual_model1_combo.clear()
            self.dual_model2_combo.clear()
            self.dual_model1_combo.addItems(available_models)
            self.dual_model2_combo.addItems(available_models)
        except Exception as e:
            error_msg = f"Error loading models: {str(e)}"
            if self.current_mode == 'solo':
                self.solo_chat_history.append(error_msg)
            else:
                self.dual_chat_history1.append(error_msg)
                self.dual_chat_history2.append(error_msg)

    def toggle_mode(self):
        if self.current_mode == 'solo':
            # Switch to dual mode
            self.mode_stack.setCurrentWidget(self.dual_mode_widget)
            self.mode_toggle_button.setText("Switch to Solo AI Mode")
            self.current_mode = 'dual'
        else:
            # Switch to solo mode
            self.mode_stack.setCurrentWidget(self.solo_mode_widget)
            self.mode_toggle_button.setText("Switch to Dual AI Mode")
            self.current_mode = 'solo'

    def send_message(self, mode):
        if mode == 'solo':
            message = self.solo_message_input.text().strip()
            if not message:
                return

            model = self.solo_model_combo.currentText()
            self.solo_chat_history.append(f"<b>You ({model}):</b> {message}")
            self.solo_message_input.clear()

            # Start chat thread
            self.solo_chat_thread = ModelChatThread(model, message)
            self.solo_chat_thread.response_signal.connect(self.display_solo_response)
            self.solo_chat_thread.start()

        elif mode == 'dual':
            message = self.dual_message_input.text().strip()
            if not message:
                return

            # Clear previous chat histories
            self.dual_chat_history1.clear()
            self.dual_chat_history2.clear()

            # Get selected models
            model1 = self.dual_model1_combo.currentText()
            model2 = self.dual_model2_combo.currentText()

            # Add user message to both chat histories
            self.dual_chat_history1.append(f"<b>You ({model1}):</b> {message}")
            self.dual_chat_history2.append(f"<b>You ({model2}):</b> {message}")
            self.dual_message_input.clear()

            # Start chat threads for both models
            self.dual_chat_thread1 = ModelChatThread(model1, message)
            self.dual_chat_thread1.response_signal.connect(self.display_dual_response)
            self.dual_chat_thread1.start()

            self.dual_chat_thread2 = ModelChatThread(model2, message)
            self.dual_chat_thread2.response_signal.connect(self.display_dual_response)
            self.dual_chat_thread2.start()

    def display_solo_response(self, model, response):
        self.solo_chat_history.append(f"<b>{model}:</b> {response}\n")

    def display_dual_response(self, model, response):
        # Determine which chat history to update based on the model
        if model == self.dual_model1_combo.currentText():
            self.dual_chat_history1.append(f"<b>{model}:</b> {response}\n")
        else:
            self.dual_chat_history2.append(f"<b>{model}:</b> {response}\n")

def main():
    app = QApplication(sys.argv)
    chat_app = OllamaChatApp()
    chat_app.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
