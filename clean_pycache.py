import os
import shutil

def remove_pycache(root_dir='.'):
    """
    Supprime récursivement tous les dossiers __pycache__ 
    et fichiers .pyc dans le projet.
    """
    for dirpath, dirnames, filenames in os.walk(root_dir):
        if '__pycache__' in dirnames:
            cache_path = os.path.join(dirpath, '__pycache__')
            shutil.rmtree(cache_path)
            print(f"Supprimé: {cache_path}")
        
        for filename in filenames:
            if filename.endswith('.pyc'):
                pyc_path = os.path.join(dirpath, filename)
                os.remove(pyc_path)
                print(f"Supprimé: {pyc_path}")

if __name__ == "__main__":
    remove_pycache()
