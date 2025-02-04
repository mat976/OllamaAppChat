# Ollama Chat Application

A simple PyQt-based graphical chat application for interacting with Ollama language models.

## Prerequisites

- Ollama installed and running
- Python 3.8+

## Installation

1. Clone the repository
2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Running the Application

```
python ollama_chat_app.py
```

## Features

- Select from installed Ollama models
- Send and receive messages
- Clear chat history
- Threaded chat to prevent UI freezing
