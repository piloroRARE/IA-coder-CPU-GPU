#!/usr/bin/env python3
"""
Tests unitaires pour le module OCR d'écriture manuscrite.
"""

import os
import unittest
import tempfile
from pathlib import Path
from PIL import Image, ImageDraw

# Ajouter le dossier parent au chemin pour les imports
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from ocr_handwriting.ocr_engine import OCREngine
from ocr_handwriting.post_processing import PostProcessor
from ocr_handwriting.printer import TextPrinter


class TestPostProcessor(unittest.TestCase):
    """Tests pour le module de post-traitement."""
    
    def setUp(self):
        """Initialise le post-processeur."""
        self.processor = PostProcessor(language="fr")
    
    def test_clean_text(self):
        """Teste le nettoyage du texte."""
        raw_text = "Bonjour   je   m'appelle   Jean.  "
        cleaned = self.processor.clean_text(raw_text)
        self.assertEqual(cleaned, "Bonjour je m'appelle Jean.")
    
    def test_correct_ocr_errors(self):
        """Teste la correction des erreurs OCR."""
        raw_text = "Bonjour 0n a1me le café!"
        corrected = self.processor.correct_ocr_errors(raw_text)
        self.assertIn("aime", corrected)
        self.assertNotIn("0n", corrected)
        self.assertNotIn("a1me", corrected)
    
    def test_structure_text(self):
        """Teste la structuration du texte."""
        raw_text = "Bonjour,je m'appelle Jean"
        structured = self.processor.structure_text(raw_text)
        self.assertIn(", ", structured)
    
    def test_process(self):
        """Teste le traitement complet."""
        raw_text = "Bonjour   0n   a1me   le   café!"
        processed = self.processor.process(raw_text)
        self.assertIn("aime", processed)
        self.assertNotIn("0n", processed)
        self.assertNotIn("  ", processed)
    
    def test_detect_language(self):
        """Teste la détection de langue."""
        french_text = "Bonjour, je m'appelle Jean. J'habite à Paris."
        english_text = "Hello, my name is John. I live in New York."
        
        self.assertEqual(self.processor.detect_language(french_text), "fr")
        self.assertEqual(self.processor.detect_language(english_text), "en")
    
    def test_batch_process(self):
        """Teste le traitement par lots."""
        texts = ["Bonjour 0n", "a1me le café"]
        processed = self.processor.batch_process(texts)
        self.assertEqual(len(processed), 2)
        self.assertIn("aime", processed[0])


class TestTextPrinter(unittest.TestCase):
    """Tests pour le module d'impression."""
    
    def setUp(self):
        """Initialise l'imprimeur."""
        self.printer = TextPrinter()
    
    def test_preview_text(self):
        """Teste l'aperçu du texte."""
        text = "Bonjour\nJe m'appelle Jean."
        preview = self.printer.preview_text(text)
        self.assertIn("Bonjour", preview)
        self.assertIn("Je m'appelle Jean.", preview)
    
    def test_preview_text_long(self):
        """Teste l'aperçu du texte avec un texte long."""
        text = "\n".join([f"Ligne {i}" for i in range(30)])
        preview = self.printer.preview_text(text, max_lines=5)
        self.assertIn("Ligne 0", preview)
        self.assertIn("Ligne 4", preview)
        self.assertIn("lignes supplémentaires", preview)
    
    def test_save_as_txt(self):
        """Teste l'enregistrement en fichier texte."""
        text = "Bonjour, je m'appelle Jean."
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
            temp_path = f.name
        
        try:
            result = self.printer.save_as_txt(text, temp_path)
            self.assertEqual(result, temp_path)
            
            # Vérifier que le fichier existe
            self.assertTrue(os.path.exists(temp_path))
            
            # Vérifier le contenu
            with open(temp_path, 'r', encoding='utf-8') as f:
                content = f.read()
            self.assertEqual(content, text)
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_save_as_pdf(self):
        """Teste l'enregistrement en PDF."""
        if not self.printer.fpdf_available:
            self.skipTest("La bibliothèque fpdf n'est pas disponible.")
        
        text = "Bonjour, je m'appelle Jean."
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
            temp_path = f.name
        
        try:
            result = self.printer.save_as_pdf(text, temp_path, title="Test")
            self.assertEqual(result, temp_path)
            
            # Vérifier que le fichier existe
            self.assertTrue(os.path.exists(temp_path))
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)


class TestOCREngine(unittest.TestCase):
    """Tests pour le moteur OCR."""
    
    def setUp(self):
        """Initialise le moteur OCR."""
        self.ocr = OCREngine(engine="easyocr", languages=["fr"])
    
    def tearDown(self):
        """Ferme le moteur OCR."""
        self.ocr.close()
    
    def test_preprocess_image(self):
        """Teste le prétraitement d'image."""
        # Créer une image de test
        image = Image.new('RGB', (100, 100), color='white')
        draw = ImageDraw.Draw(image)
        draw.text((10, 10), "Bonjour", fill='black')
        
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            image.save(f.name)
            temp_path = f.name
        
        try:
            processed = self.ocr.preprocess_image(temp_path)
            self.assertIsNotNone(processed)
            self.assertEqual(processed.shape[0], 100)
            self.assertEqual(processed.shape[1], 100)
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_recognize_text_with_easyocr(self):
        """Teste la reconnaissance de texte avec EasyOCR."""
        # Créer une image de test avec du texte clair
        image = Image.new('RGB', (400, 200), color='white')
        draw = ImageDraw.Draw(image)
        
        # Utiliser une police plus grande pour une meilleure reconnaissance
        try:
            font = ImageFont.truetype("arial.ttf", 30)
        except:
            font = ImageFont.load_default()
        
        draw.text((50, 50), "Bonjour Jean", fill='black', font=font)
        
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            image.save(f.name)
            temp_path = f.name
        
        try:
            results = self.ocr.recognize_text(temp_path, preprocess=False)
            self.assertIsInstance(results, list)
            self.assertGreater(len(results), 0)
            
            # Vérifier que le texte contient au moins une partie du texte original
            recognized_text = " ".join([r["text"] for r in results])
            self.assertIn("Bonjour" or "Jean" or "bonjour" or "jean", recognized_text.lower())
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)


class TestIntegration(unittest.TestCase):
    """Tests d'intégration pour le module OCR complet."""
    
    def test_full_pipeline(self):
        """Teste le pipeline complet : OCR -> Post-traitement -> Impression."""
        # Créer une image de test
        image = Image.new('RGB', (400, 200), color='white')
        draw = ImageDraw.Draw(image)
        
        try:
            font = ImageFont.truetype("arial.ttf", 30)
        except:
            font = ImageFont.load_default()
        
        draw.text((50, 50), "Bonjour Jean", fill='black', font=font)
        
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            image.save(f.name)
            temp_path = f.name
        
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
            output_path = f.name
        
        try:
            # Étape 1 : OCR
            ocr = OCREngine(engine="easyocr", languages=["fr"])
            raw_text = ocr.recognize_handwriting(temp_path)
            ocr.close()
            
            # Étape 2 : Post-traitement
            processor = PostProcessor(language="fr")
            processed_text = processor.process(raw_text)
            
            # Étape 3 : Impression
            printer = TextPrinter()
            result = printer.save_as_txt(processed_text, output_path)
            
            # Vérifier que le fichier a été créé
            self.assertTrue(os.path.exists(output_path))
            
            # Vérifier que le fichier contient du texte
            with open(output_path, 'r', encoding='utf-8') as f:
                content = f.read()
            self.assertGreater(len(content), 0)
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
            if os.path.exists(output_path):
                os.unlink(output_path)


if __name__ == '__main__':
    unittest.main()
