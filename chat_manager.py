import os
import json
import uuid
from datetime import datetime

class ChatManager:
    def __init__(self, chats_dir='chats'):
        """
        Initialize chat manager with a directory for storing chats
        
        Args:
            chats_dir (str): Directory to store chat files
        """
        self.chats_dir = os.path.abspath(chats_dir)
        os.makedirs(self.chats_dir, exist_ok=True)

    def create_new_chat(self, model):
        """
        Create a new chat session
        
        Args:
            model (str): AI model for the chat session
        
        Returns:
            dict: Chat session details
        """
        chat_id = str(uuid.uuid4())
        chat = {
            'id': chat_id,
            'model': model,
            'created_at': datetime.now().isoformat(),
            'messages': []
        }
        
        # Save the new chat
        self.save_chat(chat)
        
        return chat

    def add_message(self, chat, role, content):
        """
        Add a message to an existing chat session
        
        Args:
            chat (dict): Existing chat session
            role (str): Message role (user/assistant)
            content (str): Message content
        
        Returns:
            dict: Updated chat session
        """
        message = {
            'role': role,
            'content': content,
            'timestamp': datetime.now().isoformat()
        }
        
        chat['messages'].append(message)
        
        # Save the updated chat
        self.save_chat(chat)
        
        return chat

    def save_chat(self, chat):
        """
        Save a chat session to file
        
        Args:
            chat (dict): Chat session to save
        """
        chat_file = os.path.join(self.chats_dir, f"{chat['id']}.json")
        
        with open(chat_file, 'w', encoding='utf-8') as f:
            json.dump(chat, f, ensure_ascii=False, indent=4)

    def load_chat(self, chat_id):
        """
        Load a chat session from file
        
        Args:
            chat_id (str): Unique identifier for the chat
        
        Returns:
            dict: Loaded chat session or None if not found
        """
        chat_file = os.path.join(self.chats_dir, f"{chat_id}.json")
        
        if not os.path.exists(chat_file):
            return None
        
        with open(chat_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def list_chats(self):
        """
        List all saved chat sessions
        
        Returns:
            list: List of chat sessions
        """
        chats = []
        for filename in os.listdir(self.chats_dir):
            if filename.endswith('.json'):
                chat_path = os.path.join(self.chats_dir, filename)
                with open(chat_path, 'r', encoding='utf-8') as f:
                    chats.append(json.load(f))
        
        # Sort chats by creation time, most recent first
        return sorted(chats, key=lambda x: x.get('created_at', ''), reverse=True)

    def delete_chat(self, chat_id):
        """
        Delete a specific chat session
        
        Args:
            chat_id (str): Unique identifier for the chat
        """
        chat_file = os.path.join(self.chats_dir, f"{chat_id}.json")
        
        if os.path.exists(chat_file):
            os.remove(chat_file)
