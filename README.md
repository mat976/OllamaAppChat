# 🤖 Ollama AI Chat App

## 🌟 Présentation du Projet

### Une application de chat conversationnel alimentée par l'IA locale


## 🚀 Fonctionnalités Principales

- **Chat IA Local** : Conversations avec des modèles Ollama hébergés localement
- **Interface Moderne** : Design épuré et responsive
- **Gestion Avancée des Chats** : Sauvegarde, liste et navigation entre les conversations
- **Support Markdown** : Rendu riche des messages avec coloration syntaxique

## 🎥 Inspirations et Sources

### Vidéos YouTube

1. **Interface Utilisateur et UX**
   - [Make Tkinter Look 10x Better in 5 Minutes (CustomTkinter)](https://www.youtube.com/watch?v=Miydkti_QVE)

2. **Développement de Chatbots**
   - [Create a LOCAL Python AI Chatbot In Minutes Using Ollama](https://www.youtube.com/watch?v=d0o89z134CQ)

## 🛠 Technologies Utilisées

- **Langage** : Python 3.10+
- **Interface Graphique** : CustomTkinter
- **IA Locale** : Ollama
- **Parsing** : Markdown, Pygments
- **Gestion des Chats** : JSON, UUID

## 🏗 Architecture du Projet

```
ollama_chat_app/
│
├── main.py                   # Point d'entrée principal
│
├── chat_ui/
│   ├── ui/                   # Composants d'interface
│   │   ├── app.py            # Fenêtre principale
│   │   ├── message_display.py# Affichage des messages
│   │   └── ...
│   │
│   ├── utils/                # Utilitaires
│   │   └── markdown_parser.py# Parseur Markdown
│   │
│   └── chat_manager/         # Gestion des conversations
│       └── manager.py        # Logique de sauvegarde/chargement
│
├── models/                   # Interactions modèles IA
└── requirements.txt          # Dépendances du projet
```

## 🔧 Installation

```bash
# Cloner le dépôt
git clone https://github.com/votre-username/OllamaAppChat.git


# Installer les dépendances
pip install -r requirements.txt

# Lancer l'application
python main.py
```
