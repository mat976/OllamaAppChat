import threading
import queue
from models import ModelChatThread

class InputHandler:
    def __init__(self, app):
        self.app = app

    def send_message(self, message):
        """
        Send a message in the current chat
        
        Args:
            message (str): Message to send
        """
        # Clear input
        self.app.message_entry.delete(0, 'end')

        # Disable input during processing
        self.app.message_entry.configure(state='disabled')
        self.app.send_button.configure(state='disabled')

        # Start thinking animation
        self.start_thinking()

        # Add user message to chat
        self.app.current_chat = self.app.chat_manager.add_message(
            self.app.current_chat, 'user', message
        )
        self.app.message_display.display_message('user', message)

        # Prepare messages for model
        messages = self.app.current_chat['messages']

        # Start chat thread
        thread = ModelChatThread(
            self.app.current_chat['model'], 
            messages, 
            self.app.response_queue
        )
        thread.start()

    def start_thinking(self):
        """
        Start the thinking animation in the chat.
        Displays a spinning indicator while processing.
        """
        # Stop any existing animation
        self.stop_thinking()
        
        # Set animation flag
        self.app.animation_running = True
        
        # Display initial thinking message
        self.app.message_display.display_message("assistant", "🤖 Thinking...", is_animation=True)
        
        # Start animation thread
        self.app.animation_thread = threading.Thread(
            target=self._animate_thinking, 
            daemon=True
        )
        self.app.animation_thread.start()

    def _animate_thinking(self):
        """
        Internal method to animate the thinking indicator.
        Uses a spinner animation with different characters.
        """
        spinners = ["|", "/", "-", "\\"]
        spinner_index = 0
        
        while self.app.animation_running:
            # Update thinking message with spinner
            spinner = spinners[spinner_index % len(spinners)]
            self.update_last_message(f"🤖 Thinking {spinner}")
            
            # Increment spinner and pause
            spinner_index += 1
            import time
            time.sleep(0.2)

    def stop_thinking(self):
        """
        Stop the thinking animation and remove the thinking message.
        """
        # Stop animation thread
        self.app.animation_running = False
        if self.app.animation_thread and self.app.animation_thread.is_alive():
            self.app.animation_thread.join(timeout=0.5)
        
        # Remove last message if it's an animation
        self.delete_last_message(is_animation=True)

    def update_last_message(self, new_content):
        """
        Update the last message in the chat text.
        
        Args:
            new_content (str): New content to replace the last message
        """
        try:
            self.app.chat_text.configure(state="normal")
            
            # Find the last line
            last_line = self.app.chat_text.index("end-2l")
            
            # Delete the last line and insert new content
            self.app.chat_text.delete(last_line, "end-1c")
            self.app.chat_text.insert("end", f"{new_content}\n", "ai_tag")
            
            self.app.chat_text.configure(state="disabled")
            self.app.chat_text.see("end")
        except Exception as e:
            print(f"Error updating last message: {e}")

    def delete_last_message(self, is_animation=False):
        """
        Delete the last message from the chat text.
        
        Args:
            is_animation (bool): Flag to indicate if deleting an animation message
        """
        try:
            self.app.chat_text.configure(state="normal")
            
            # If deleting an animation message, look for "Thinking" in the last line
            if is_animation:
                last_line_content = self.app.chat_text.get("end-2l", "end-1c")
                if "Thinking" in last_line_content:
                    self.app.chat_text.delete("end-2l", "end-1c")
            else:
                # Delete the last line unconditionally
                self.app.chat_text.delete("end-2l", "end-1c")
            
            self.app.chat_text.configure(state="disabled")
            self.app.chat_text.see("end")
        except Exception as e:
            print(f"Error deleting last message: {e}")

    def handle_ai_response(self, response, think_content):
        """
        Handle AI response with improved display and interaction
        
        Args:
            response (str): AI's response message
            think_content (str, optional): Internal thought content
        """
        # Stop thinking animation
        self.stop_thinking()
        
        # Display response in main thread
        self.app.message_display.display_message('assistant', response, think_content)
        
        # Re-enable input
        self.app.message_entry.configure(state='normal')
        self.app.send_button.configure(state='normal')
        
        # Focus back on message entry
        self.app.message_entry.focus_set()
