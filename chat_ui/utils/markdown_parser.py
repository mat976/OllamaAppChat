import re
import pygments
from pygments.lexers import get_lexer_by_name
from pygments.formatters import BBCodeFormatter

class MarkdownParser:
    @classmethod
    def parse_markdown(cls, text):
        """
        Parse markdown text into segments with different types.
        
        Args:
            text (str): Markdown-formatted text to parse
        
        Returns:
            list: List of segments with type and content
        """
        segments = []
        pattern = r'(\*\*.*?\*\*|\*.*?\*|`.*?`|```[\s\S]*?```)'
        last_end = 0

        for match in re.finditer(pattern, text):
            # Add normal text before the match
            if match.start() > last_end:
                segments.append({
                    'type': 'normal', 
                    'content': text[last_end:match.start()]
                })

            # Process the matched markdown segment
            matched_text = match.group(0)
            if matched_text.startswith('**') and matched_text.endswith('**'):
                # Bold text
                segments.append({
                    'type': 'bold', 
                    'content': matched_text[2:-2]
                })
            elif matched_text.startswith('*') and matched_text.endswith('*'):
                # Italic text
                segments.append({
                    'type': 'italic', 
                    'content': matched_text[1:-1]
                })
            elif matched_text.startswith('`') and matched_text.endswith('`') and not matched_text.startswith('```'):
                # Inline code
                segments.append({
                    'type': 'code', 
                    'content': matched_text[1:-1]
                })
            elif matched_text.startswith('```'):
                # Code block
                code_lines = matched_text[3:-3].split('\n')
                language = code_lines[0].strip() if code_lines else 'text'
                code_content = '\n'.join(code_lines[1:])
                segments.append({
                    'type': 'code_block', 
                    'content': code_content,
                    'language': language
                })

            last_end = match.end()

        # Add remaining text after the last match
        if last_end < len(text):
            segments.append({
                'type': 'normal', 
                'content': text[last_end:]
            })

        return segments

    @classmethod
    def highlight_code(cls, code, language='text'):
        """
        Highlight code using Pygments.
        
        Args:
            code (str): Code to highlight
            language (str, optional): Programming language. Defaults to 'text'.
        
        Returns:
            str: Highlighted code
        """
        try:
            lexer = get_lexer_by_name(language)
            formatter = BBCodeFormatter()
            return pygments.highlight(code, lexer, formatter)
        except Exception:
            return code  # Fallback if highlighting fails
