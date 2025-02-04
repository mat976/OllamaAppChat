import ollama
import threading
import queue
import re
import traceback
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='ollama_chat.log',
    filemode='a'
)

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
            logging.error(f"Error retrieving models: {e}")
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
            # Special handling for DeepSeek model
            if 'deepseek' in model.lower():
                messages = OllamaModelHandler._prepare_deepseek_messages(messages)
            
            logging.debug(f"Sending messages to model {model}: {messages}")
            
            response = ollama.chat(
                model=model, 
                messages=messages
            )
            
            logging.debug(f"Received response from {model}: {response}")
            return response['message']['content']
        except Exception as e:
            logging.error(f"Error generating response: {e}")
            logging.error(traceback.format_exc())
            return f"Error generating response: {e}"

    @staticmethod
    def _prepare_deepseek_messages(messages):
        """
        Prepare messages for DeepSeek model with special formatting
        
        Args:
            messages (list): Original conversation messages
        
        Returns:
            list: Formatted messages for DeepSeek
        """
        formatted_messages = []
        
        # Add system message if exists
        system_message = next((msg for msg in messages if msg.get('role') == 'system'), None)
        if system_message:
            formatted_messages.append({
                'role': 'system',
                'content': system_message['content']
            })
        
        # Format user and assistant messages
        for msg in messages:
            if msg['role'] == 'user':
                formatted_messages.append({
                    'role': 'user',
                    'content': f"<｜User｜>{msg['content']}"
                })
            elif msg['role'] == 'assistant':
                formatted_messages.append({
                    'role': 'assistant',
                    'content': f"<｜Assistant｜>{msg['content']}"
                })
        
        return formatted_messages

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

    def _extract_think_content(self, response):
        """
        Extract content from <think> tags
        
        Args:
            response (str): Full model response
        
        Returns:
            tuple: (main_response, think_content)
        """
        try:
            # Extract <think> content
            think_matches = re.findall(r'<think>(.*?)</think>', response, re.DOTALL)
            think_content = think_matches[0] if think_matches else ""
            
            # Remove <think> tags from the main response
            main_response = re.sub(r'<think>.*?</think>', '', response, flags=re.DOTALL).strip()
            
            return main_response, think_content
        except Exception as e:
            logging.error(f"Error extracting think content: {e}")
            logging.error(traceback.format_exc())
            return response, ""

    def _clean_response(self, response):
        """
        Clean the model's response by removing tags and extra whitespace
        
        Args:
            response (str): Raw model response
        
        Returns:
            str: Cleaned response
        """
        try:
            # Remove DeepSeek specific tags and other XML-like tags
            response = re.sub(r'<｜[^>]+｜>', '', response, flags=re.DOTALL)
            
            # Remove extra whitespace
            response = re.sub(r'\s+', ' ', response).strip()
            
            return response
        except Exception as e:
            logging.error(f"Error cleaning response: {e}")
            logging.error(traceback.format_exc())
            return response

    def _run(self):
        """
        Run the chat generation in a separate thread
        Streams and collects the full response
        """
        try:
            logging.debug(f"Starting chat thread for model {self.model}")
            logging.debug(f"Messages: {self.messages}")
            
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
            
            logging.debug(f"Full response received: {full_response}")
            
            # Clean and extract think content
            main_response, think_content = self._extract_think_content(full_response)
            
            # Clean the final response
            final_clean_response = self._clean_response(main_response)
            final_clean_think = self._clean_response(think_content)
            
            logging.debug(f"Final clean response: {final_clean_response}")
            logging.debug(f"Final clean think content: {final_clean_think}")
            
            # Send the complete response with think content
            if final_clean_response:
                self.response_queue.put((
                    self.model, 
                    final_clean_response, 
                    final_clean_think, 
                    True
                ))
            else:
                logging.warning("No clean response generated")
                self.response_queue.put((
                    self.model, 
                    "I'm sorry, but I couldn't generate a meaningful response.", 
                    "", 
                    False
                ))
        
        except Exception as e:
            # Error handling
            error_msg = f"Error in chat with {self.model}: {str(e)}"
            logging.error(error_msg)
            logging.error(traceback.format_exc())
            self.response_queue.put((self.model, error_msg, "", False))

class ResponseSignal:
    def __init__(self):
        self.callbacks = []

    def connect(self, callback):
        self.callbacks.append(callback)

    def emit(self, model, response):
        for callback in self.callbacks:
            callback(model, response)
