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
- New feature: Support for multiple chat windows
- New feature: Option to save chat logs to file

## Usage

- Start the application and select an Ollama model
- Type a message and press send to receive a response
- Use the "Clear Chat" button to clear the chat history
- Use the "Save Chat Log" button to save the chat history to a file
