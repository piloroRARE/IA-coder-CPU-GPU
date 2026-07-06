#!/usr/bin/env python3
"""
Script pour générer une image de test avec du texte manuscrit simulé.

Ce script crée une image PNG avec du texte qui ressemble à de l'écriture manuscrite
pour tester le module OCR.
"""

import os
from PIL import Image, ImageDraw, ImageFont
import random


def generate_handwriting_image(text: str, output_path: str = "test_handwriting.png", size: tuple = (800, 400)):
    """
    Génère une image avec du texte simulant une écriture manuscrite.
    
    Args:
        text: Texte à écrire sur l'image.
        output_path: Chemin de sortie pour l'image.
        size: Taille de l'image (largeur, hauteur).
    """
    # Créer une image blanche
    image = Image.new('RGB', size, color='white')
    draw = ImageDraw.Draw(image)
    
    # Charger une police qui ressemble à une écriture manuscrite
    # (si disponible, sinon utiliser une police par défaut)
    try:
        # Essayer de charger une police manuscrite (ex: "Comic Sans MS" ou "Dancing Script")
        font = ImageFont.truetype("arial.ttf", 32)
    except:
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/arial.ttf", 32)
        except:
            font = ImageFont.load_default()
    
    # Diviser le texte en lignes
    lines = text.split('\n')
    
    # Position de départ
    x, y = 50, 50
    line_height = 40
    
    # Dessiner chaque ligne avec un léger décalage pour simuler l'écriture manuscrite
    for line in lines:
        # Ajouter un léger décalage aléatoire pour chaque caractère
        for i, char in enumerate(line):
            # Calculer la position du caractère
            char_width = draw.textlength(char, font=font)
            
            # Ajouter un décalage aléatoire (simulation de l'écriture manuscrite)
            offset_x = random.uniform(-2, 2)
            offset_y = random.uniform(-2, 2)
            
            # Dessiner le caractère
            draw.text((x + offset_x, y + offset_y), char, fill='black', font=font)
            
            # Avancer à la position suivante
            x += char_width + random.uniform(-5, 5)
        
        # Passer à la ligne suivante
        x = 50
        y += line_height + random.uniform(-5, 5)
    
    # Sauvegarder l'image
    image.save(output_path)
    print(f"✅ Image générée: {output_path}")
    return output_path


if __name__ == "__main__":
    # Texte de test en français
    test_text = """
Bonjour, je m'appelle Jean.
J'ai 25 ans et j'habite à Paris.
J'aime lire des livres et boire du café.
Aujourd'hui, il fait beau.
Je vais me promener dans le parc.
"""
    
    # Générer l'image
    output_path = os.path.join(os.path.dirname(__file__), "test_handwriting.png")
    generate_handwriting_image(test_text, output_path)
    
    print(f"\n📝 Texte utilisé pour le test:\n{test_text}")
    print(f"\n🖼️ Image générée: {output_path}")
    print("\n💡 Vous pouvez maintenant utiliser cette image pour tester le module OCR:")
    print(f"   python -c \"from ocr_handwriting.ocr_engine import OCREngine; ocr = OCREngine(); print(ocr.recognize_handwriting('{output_path}')); ocr.close()\"")
