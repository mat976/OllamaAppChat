import uuid
import os
import json
import queue
import threading
from datetime import datetime

class ChatManager:
    def __init__(self, chats_dir='chats'):
        """
        Initialize ChatManager with a directory for storing chats
        
        Args:
            chats_dir (str, optional): Directory to store chat files. Defaults to 'chats'.
        """
        self.chats_dir = os.path.abspath(chats_dir)
        
        # Create chats directory if it doesn't exist
        os.makedirs(self.chats_dir, exist_ok=True)
        
        # Initialize chats dictionary
        self.chats = {}
        self._load_existing_chats()

    def _load_existing_chats(self):
        """
        Load existing chat files from the chats directory
        """
        for filename in os.listdir(self.chats_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(self.chats_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        chat = json.load(f)
                        self.chats[chat['id']] = chat
                except (json.JSONDecodeError, KeyError) as e:
                    print(f"Error loading chat file {filename}: {e}")

    def create_new_chat(self, model=None):
        """
        Create a new chat session.
        
        Args:
            model (str, optional): Model to use for the chat. Defaults to None.
        
        Returns:
            dict: Newly created chat session
        """
        chat_id = str(uuid.uuid4())
        chat = {
            'id': chat_id,
            'model': model,
            'messages': [],
            'created_at': datetime.now().isoformat(),
            'last_updated': datetime.now().isoformat()
        }
        
        self.chats[chat_id] = chat
        self.save_chat(chat)
        return chat

    def add_message(self, chat, role, message):
        """
        Add a message to a chat session.
        
        Args:
            chat (dict): Chat session to add message to
            role (str): Role of the message sender ('user' or 'assistant')
            message (str): Message content
        
        Returns:
            dict: Updated chat session
        """
        message_entry = {
            'role': role,
            'content': message,
            'timestamp': datetime.now().isoformat()
        }
        
        chat['messages'].append(message_entry)
        chat['last_updated'] = datetime.now().isoformat()
        
        # Update the chat in memory and save to file
        self.chats[chat['id']] = chat
        self.save_chat(chat)
        
        return chat

    def save_chat(self, chat):
        """
        Save a chat session to a JSON file
        
        Args:
            chat (dict): Chat session to save
        """
        try:
            chat_file = os.path.join(self.chats_dir, f"{chat['id']}.json")
            
            with open(chat_file, 'w', encoding='utf-8') as f:
                json.dump(chat, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Error saving chat {chat['id']}: {e}")

    def list_chats(self):
        """
        List all available chat sessions.
        
        Returns:
            list: List of chat sessions sorted by last updated time
        """
        return sorted(
            list(self.chats.values()), 
            key=lambda chat: chat.get('last_updated', chat.get('created_at')), 
            reverse=True
        )

    def get_chat_by_id(self, chat_id):
        """
        Retrieve a specific chat by its ID.
        
        Args:
            chat_id (str): ID of the chat to retrieve
        
        Returns:
            dict: Chat session or None if not found
        """
        return self.chats.get(chat_id)

    def delete_chat(self, chat_id):
        """
        Delete a specific chat session.
        
        Args:
            chat_id (str): ID of the chat to delete
        """
        if chat_id in self.chats:
            # Remove from memory
            del self.chats[chat_id]
            
            # Remove from file system
            chat_file = os.path.join(self.chats_dir, f"{chat_id}.json")
            if os.path.exists(chat_file):
                os.remove(chat_file)

    def get_chat_messages(self, chat):
        """
        Get messages from a chat session.
        
        Args:
            chat (dict): Chat session to retrieve messages from
        
        Returns:
            list: List of messages in the chat
        """
        return chat.get('messages', [])

    def process_responses(self, callback):
        """
        Process responses from a queue in a separate thread.
        
        Args:
            callback (callable): Function to call with each response
        """
        # Initialize response queue if not already created
        if not hasattr(self, 'response_queue'):
            self.response_queue = queue.Queue()
        
        # Initialize response thread if not already created
        if not hasattr(self, 'response_thread'):
            def worker():
                while True:
                    try:
                        response = self.response_queue.get(timeout=1)
                        callback(response)
                        self.response_queue.task_done()
                    except queue.Empty:
                        break

            self.response_thread = threading.Thread(target=worker, daemon=True)
            self.response_thread.start()

    def add_response_to_queue(self, response):
        """
        Add a response to the processing queue.
        
        Args:
            response (dict): Response to add to the queue
        """
        # Initialize response queue if not already created
        if not hasattr(self, 'response_queue'):
            self.response_queue = queue.Queue()
        
        self.response_queue.put(response)
