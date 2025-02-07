from PIL import Image, ImageDraw, ImageFont
import os

# Créer une image
width, height = 500, 500
image = Image.new('RGB', (width, height), color='white')
draw = ImageDraw.Draw(image)

# Dessiner un arrière-plan dégradé
for y in range(height):
    r = int(255 * (1 - y / height))
    g = int(100 * (1 - y / height))
    b = int(200 * (1 - y / height))
    for x in range(width):
        draw.point((x, y), fill=(r, g, b))

# Dessiner un robot stylisé
draw.rectangle([150, 100, 350, 400], fill='darkblue', outline='black')
draw.ellipse([200, 50, 300, 150], fill='lightblue', outline='black')  # Tête
draw.rectangle([180, 200, 220, 350], fill='gray', outline='black')  # Bras gauche
draw.rectangle([280, 200, 320, 350], fill='gray', outline='black')  # Bras droit

# Ajouter du texte
font = ImageFont.truetype("arial.ttf", 70)
draw.text((100, 400), "Ollama", fill='white', font=font)

# Sauvegarder l'image
output_path = os.path.join('docs', 'logo.png')
image.save(output_path)
print(f"Logo sauvegardé dans {output_path}")
