import customtkinter as ctk
from chat_ui.utils.markdown_parser import MarkdownParser

class MessageDisplay:
    def __init__(self, chat_text_widget):
        self.chat_text = chat_text_widget
        self._configure_tags()

    def _configure_tags(self):
        """Configure text tags for different message types"""
        tag_configs = {
            "user_tag": {"foreground": "light blue"},
            "ai_tag": {"foreground": "light green"},
            "typing_tag": {"foreground": "gray"},
            "bold": {"foreground": "dark blue"},
            "italic": {"foreground": "dark green"},
            "code": {"background": "gray90", "foreground": "dark red"},
            "separator": {"foreground": "#CCCCCC", "justify": "center"}
        }

        for tag, config in tag_configs.items():
            self.chat_text.tag_config(tag, **config)

    def display_message(self, role, content, think_content=None, is_animation=False):
        """
        Display a message in the chat text area with advanced formatting
        
        Args:
            role (str): Message role (user/assistant)
            content (str): Message content
            think_content (str, optional): Internal thought content
            is_animation (bool, optional): Flag for animation messages
        """
        self.chat_text.configure(state="normal")

        # Determine tag and prefix based on role
        tag, prefix = self._get_tag_and_prefix(role, is_animation)

        # Insert a newline before the message if it's not the first message
        if self.chat_text.get("1.0", "end-1c").strip():
            self.chat_text.insert("end", "\n")

        # Insert message prefix
        self.chat_text.insert("end", f"{prefix}", tag)

        # Parse and insert markdown-formatted content
        segments = MarkdownParser.parse_markdown(content)
        for segment in segments:
            self._insert_segment(segment, tag)

        # Add a newline at the end
        self.chat_text.insert("end", "\n")

        # Add think button for AI messages
        if role != 'user' and think_content and think_content.strip():
            self._add_think_button(think_content)

        # Add visual separator for non-animation messages
        if not is_animation:
            self.chat_text.insert("end", "\n" + "─" * 30 + "\n", "separator")

        self.chat_text.configure(state="disabled")
        self.chat_text.see("end")

    def _get_tag_and_prefix(self, role, is_animation):
        """Determine tag and prefix based on message role"""
        if role == 'user':
            return "user_tag", "👤 Vous: "
        else:
            prefix = "🤖 AI: " if not is_animation else ""
            return "ai_tag", prefix

    def _insert_segment(self, segment, default_tag):
        """Insert a markdown segment with appropriate formatting"""
        segment_type_map = {
            'normal': default_tag,
            'bold': "bold",
            'italic': "italic",
            'code': "code",
            'code_block': "code_block_tag"
        }

        tag = segment_type_map.get(segment['type'], default_tag)

        if segment['type'] == 'code_block':
            # Special handling for code blocks
            highlighted_code = MarkdownParser.highlight_code(
                segment['content'], 
                segment['language']
            )
            self.chat_text.tag_config("code_block_tag", 
                background="gray95", 
                foreground="black"
            )
            self.chat_text.insert("end", "\n" + highlighted_code + "\n", "code_block_tag")
        else:
            self.chat_text.insert("end", segment['content'], tag)

    def _add_think_button(self, think_content):
        """Add a clickable 'thoughts' button"""
        unique_tag = f"think_button_{id(think_content)}"
        think_button_text = " 💭 Pensées "
        self.chat_text.insert("end", think_button_text, unique_tag)

        # Configure think button tag
        self.chat_text.tag_config(unique_tag, 
            foreground="blue", 
            underline=1
        )
        
        # Bind events to the think button
        self.chat_text.tag_bind(unique_tag, "<Button-1>", 
            lambda event, tc=think_content: self._show_think_content(tc)
        )
        self.chat_text.tag_bind(unique_tag, "<Enter>", 
            lambda event: self.chat_text.config(cursor="hand2")
        )
        self.chat_text.tag_bind(unique_tag, "<Leave>", 
            lambda event: self.chat_text.config(cursor="")
        )

    def _show_think_content(self, think_content):
        """Display the internal thought content"""
        # TODO: Implement a proper dialog or popup for showing think content
        print(f"Internal Thoughts: {think_content}")

    def clear_chat(self):
        """Clear the chat text area"""
        self.chat_text.configure(state="normal")
        self.chat_text.delete("1.0", "end")
        self.chat_text.configure(state="disabled")

    def load_chat_messages(self, chat):
        """Load messages for a specific chat"""
        self.clear_chat()
        
        for msg in chat.get('messages', []):
            role = msg['role']
            content = msg['content']
            
            self.display_message(role, content)

    def show_welcome_message(self):
        """Display a welcome message when no chats exist"""
        self.chat_text.configure(state="normal")
        self.chat_text.insert("1.0", "Welcome to Ollama AI Chat! 🤖\n\n")
        self.chat_text.insert("end", "To get started, click the + New Chat button to create a new chat session.\n\n")
        self.chat_text.insert("end", "You can also load existing chats from the sidebar.\n\n")
        self.chat_text.configure(state="disabled")
