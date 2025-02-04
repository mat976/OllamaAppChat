# Ollama Chat App

## Projet CDA8 - Matisse Demontis

### Description
Cette application de chat utilise Ollama pour interagir avec différents modèles de langage AI. Elle offre deux modes de conversation : mode solo et mode comparaison.

### Fonctionnalités
- Mode Solo : Conversation avec un modèle AI unique
- Mode Dual : Comparaison des réponses de deux modèles AI différents
- Sélection dynamique des modèles disponibles
- Interface utilisateur intuitive avec PyQt6

### Prérequis
- Python 3.8+
- Ollama installé et configuré
- Bibliothèques Python listées dans `requirements.txt`

### Installation

1. Clonez le dépôt :
```bash
git clone https://github.com/votre-username/OllamaAppChat.git
cd OllamaAppChat
```

2. Installez les dépendances :
```bash
pip install -r requirements.txt
```

3. Assurez-vous qu'Ollama est en cours d'exécution :
```bash
ollama serve  # Ou la commande appropriée pour démarrer Ollama
```

### Lancement de l'Application

```bash
python main.py
```

### Structure du Projet
- `main.py` : Point d'entrée de l'application
- `chat_ui.py` : Interface utilisateur et logique de chat
- `models.py` : Gestion des threads de chat

### Modes de Conversation
1. **Mode Solo** : 
   - Sélectionnez un modèle
   - Envoyez des messages
   - Recevez des réponses du modèle sélectionné

2. **Mode Dual** : 
   - Sélectionnez deux modèles
   - Comparez leurs réponses à la même question

### Dépannage
- Assurez-vous qu'Ollama est correctement installé
- Vérifiez que des modèles sont disponibles
- Consultez les messages d'erreur dans l'interface

### Auteur
Matisse Demontis - Projet CDA8

### Licence
[À spécifier - par exemple MIT, Apache, etc.]
