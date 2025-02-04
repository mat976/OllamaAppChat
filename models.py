import ollama
import threading
import queue
import re

class OllamaModelHandler:
    @staticmethod
    def get_available_models():
        """
        Retrieve a list of available Ollama models
        
        Returns:
            list: Names of available models
        """
        try:
            models = ollama.list()
            return [model['name'] for model in models['models']]
        except Exception as e:
            print(f"Error retrieving models: {e}")
            return []

    @staticmethod
    def generate_response(model, messages):
        """
        Generate a response from the specified model
        
        Args:
            model (str): Name of the Ollama model
            messages (list): Conversation history
        
        Returns:
            str: Generated response
        """
        try:
            response = ollama.chat(
                model=model, 
                messages=messages
            )
            return response['message']['content']
        except Exception as e:
            return f"Error generating response: {e}"

class ModelChatThread:
    def __init__(self, model, messages, response_queue):
        """
        Initialize a chat thread for generating model responses
        
        Args:
            model (str): Name of the Ollama model
            messages (list): Conversation history
            response_queue (queue.Queue): Queue to send responses
        """
        self.model = model
        self.messages = messages
        self.response_queue = response_queue
        self._thread = None

    def start(self):
        """Start the chat thread"""
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def _clean_response(self, response):
        """
        Clean the model's response by removing tags and extra whitespace
        
        Args:
            response (str): Raw model response
        
        Returns:
            str: Cleaned response
        """
        # Remove <think> tags and other XML-like tags
        response = re.sub(r'<[^>]+>', '', response, flags=re.DOTALL)
        
        # Remove extra whitespace
        response = re.sub(r'\s+', ' ', response).strip()
        
        return response

    def _run(self):
        """
        Run the chat generation in a separate thread
        Streams and collects the full response
        """
        try:
            # Stream the response
            full_response = ""
            for chunk in ollama.chat(
                model=self.model, 
                messages=self.messages,
                stream=True
            ):
                if chunk['done']:
                    break
                if 'message' in chunk:
                    part = chunk['message'].get('content', '')
                    full_response += part
            
            # Clean the final response
            final_clean_response = self._clean_response(full_response)
            
            # Send the complete response with a special marker
            if final_clean_response:
                self.response_queue.put((self.model, final_clean_response, True))
        
        except Exception as e:
            # Error handling
            error_msg = f"Error in chat with {self.model}: {str(e)}"
            self.response_queue.put((self.model, error_msg, False))

class ResponseSignal:
    def __init__(self):
        self.callbacks = []

    def connect(self, callback):
        self.callbacks.append(callback)

    def emit(self, model, response):
        for callback in self.callbacks:
            callback(model, response)
