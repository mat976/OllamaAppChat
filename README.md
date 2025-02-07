# Ollama Chat App

## Description
Une application de chat conversationnel utilisant Ollama et CustomTkinter.

## Structure du Projet
```
ollama_chat_app/
│
├── .gitignore
├── main.py
│
├── chat_ui/
│   ├── __init__.py
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── app.py
│   │   ├── markdown_parser.py
│   │   ├── message_display.py
│   │   ├── input_area.py
│   │   └── chat_list.py
│   │
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── threading_utils.py
│   │   └── animation_utils.py
│   │
│   └── config/
│       ├── __init__.py
│       └── appearance.py
│
├── requirements.txt
└── README.md
```

## Installation

1. Clonez le dépôt
2. Créez un environnement virtuel
3. Installez les dépendances :
   ```bash
   pip install -r requirements.txt
   ```

## Utilisation

```bash
python main.py
```

## Nettoyage des Caches

Pour supprimer les fichiers `__pycache__` :

```bash
python clean_pycache.py
```

## Licence
[À DÉFINIR]
