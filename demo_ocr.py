#!/usr/bin/env python3
"""
Script de démonstration pour le module OCR d'écriture manuscrite.

Ce script montre comment utiliser le module OCR pour reconnaître
du texte dans des images et l'imprimer/enregistrer.
"""

import os
import sys
from pathlib import Path

# Ajouter le dossier courant au chemin
sys.path.insert(0, os.path.dirname(__file__))

from ocr_handwriting import PostProcessor, TextPrinter


def demo_post_processing():
    """Démonstration du post-traitement."""
    print("\n" + "="*60)
    print("📝 DÉMONSTRATION : Post-traitement du texte")
    print("="*60)
    
    processor = PostProcessor(language="fr")
    
    # Exemple 1 : Texte avec des erreurs OCR courantes
    raw_text1 = "Bonjour 0n a1me le café! J4i 25 4ns."
    print(f"\n📄 Texte brut: {raw_text1}")
    cleaned_text1 = processor.process(raw_text1)
    print(f"✅ Texte traité: {cleaned_text1}")
    
    # Exemple 2 : Texte avec des caractères spéciaux
    raw_text2 = "C'est l'été! Il fait beau aujourd'hui."
    print(f"\n📄 Texte brut: {raw_text2}")
    cleaned_text2 = processor.process(raw_text2)
    print(f"✅ Texte traité: {cleaned_text2}")
    
    # Exemple 3 : Détection de langue
    french_text = "Bonjour, je m'appelle Jean. J'habite à Paris."
    english_text = "Hello, my name is John. I live in New York."
    
    print(f"\n🌍 Détection de langue:")
    print(f"   Texte français: {processor.detect_language(french_text)} ✅")
    print(f"   Texte anglais: {processor.detect_language(english_text)} ✅")


def demo_printer():
    """Démonstration de l'impression."""
    print("\n" + "="*60)
    print("🖨️  DÉMONSTRATION : Impression et enregistrement")
    print("="*60)
    
    printer = TextPrinter()
    
    # Texte à imprimer
    text = """
Bonjour, je m'appelle Jean.
J'ai 25 ans et j'habite à Paris.
J'aime lire des livres et boire du café.
Aujourd'hui, il fait beau.
    """
    
    print(f"\n📄 Texte à traiter:\n{text}")
    
    # Aperçu
    preview = printer.preview_text(text, max_lines=3)
    print(f"\n👀 Aperçu (3 lignes):\n{preview}")
    
    # Enregistrer en fichier texte
    output_dir = Path("ocr_handwriting/output")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    txt_path = output_dir / "demo_output.txt"
    result = printer.save_as_txt(text, txt_path)
    
    if result:
        print(f"\n✅ Fichier texte généré: {txt_path}")
        print(f"   Taille: {os.path.getsize(txt_path)} octets")
    else:
        print("\n❌ Échec de la génération du fichier texte")
    
    # Essayer de générer un PDF (si fpdf est disponible)
    pdf_path = output_dir / "demo_output.pdf"
    result = printer.save_as_pdf(text, pdf_path, title="Démonstration OCR")
    
    if result:
        print(f"✅ PDF généré: {pdf_path}")
        print(f"   Taille: {os.path.getsize(pdf_path)} octets")
    else:
        print("⚠️  La bibliothèque fpdf n'est pas disponible. Impossible de générer le PDF.")


def demo_ocr_engine():
    """Démonstration du moteur OCR (si EasyOCR est disponible)."""
    print("\n" + "="*60)
    print("🔍 DÉMONSTRATION : Moteur OCR")
    print("="*60)
    
    try:
        from ocr_handwriting import OCREngine
        
        # Initialiser le moteur OCR
        print("\n🔄 Initialisation du moteur OCR (EasyOCR)...")
        ocr = OCREngine(engine="easyocr", languages=["fr"])
        print("✅ Moteur OCR initialisé avec succès!")
        
        # Vérifier si des exemples existent
        examples_dir = Path("ocr_handwriting/examples")
        if examples_dir.exists():
            images = list(examples_dir.glob("*.png")) + list(examples_dir.glob("*.jpg"))
            if images:
                print(f"\n📁 Images de test trouvées: {len(images)}")
                for img in images[:3]:  # Limiter à 3 images
                    print(f"   - {img.name}")
                    try:
                        text = ocr.recognize_handwriting(img)
                        print(f"     Texte reconnu: {text[:50]}...")
                    except Exception as e:
                        print(f"     ❌ Erreur: {e}")
            else:
                print("\n⚠️  Aucune image de test trouvée dans le dossier 'examples'")
                print("   Vous pouvez en ajouter ou utiliser le script generate_test_image.py")
        else:
            print("\n⚠️  Le dossier 'examples' n'existe pas")
        
        # Fermer le moteur OCR
        ocr.close()
        print("\n🔄 Moteur OCR fermé")
        
    except ImportError as e:
        print(f"\n❌ Impossible d'importer EasyOCR: {e}")
        print("   Installez-le avec: pip install easyocr")
    except Exception as e:
        print(f"\n❌ Erreur lors de l'initialisation du moteur OCR: {e}")


def main():
    """Fonction principale de démonstration."""
    print("\n" + "="*60)
    print("🚀 DÉMONSTRATION DU MODULE OCR D'ÉCRITURE MANUSCRITE")
    print("="*60)
    print("\nCe script démontre les fonctionnalités du module OCR:")
    print("  1. Post-traitement du texte")
    print("  2. Impression et enregistrement")
    print("  3. Moteur OCR (si disponible)")
    
    # Démarrer les démonstrations
    demo_post_processing()
    demo_printer()
    demo_ocr_engine()
    
    print("\n" + "="*60)
    print("✅ DÉMONSTRATION TERMINÉE")
    print("="*60)
    print("\nPour aller plus loin:")
    print("  - Consultez le README.md dans ocr_handwriting/")
    print("  - Lancez l'API Flask: python -m ocr_handwriting.app")
    print("  - Exécutez les tests: python -m pytest tests/test_ocr_handwriting.py")
    print()


if __name__ == "__main__":
    main()
