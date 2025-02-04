import ollama
from PyQt6.QtCore import QThread, pyqtSignal
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
