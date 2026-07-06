#!/usr/bin/env python3
"""
Moteur OCR pour la reconnaissance d'écriture manuscrite.

Utilise EasyOCR (pour l'écriture manuscrite) et Tesseract (pour le texte imprimé).
"""

import os
import cv2
import numpy as np
from typing import List, Dict, Optional, Union
from pathlib import Path
import yaml


class OCREngine:
    """
    Classe principale pour la reconnaissance OCR.
    
    Attributes:
        engine (str): Moteur OCR utilisé ('easyocr' ou 'tesseract').
        languages (List[str]): Langues supportées.
        reader: Instance du lecteur OCR (EasyOCR ou Tesseract).
    """
    
    def __init__(self, engine: str = "easyocr", languages: List[str] = ["fr", "en"], config_path: Optional[str] = None):
        """
        Initialise le moteur OCR.
        
        Args:
            engine: Moteur OCR à utiliser ('easyocr' ou 'tesseract').
            languages: Liste des langues à supporter (ex: ['fr', 'en']).
            config_path: Chemin vers le fichier de configuration YAML.
        """
        self.engine = engine
        self.languages = languages
        self.config_path = config_path
        self.reader = None
        self._load_config()
        self._initialize_reader()
    
    def _load_config(self) -> None:
        """Charge la configuration depuis un fichier YAML."""
        if self.config_path and os.path.exists(self.config_path):
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                if config:
                    self.engine = config.get('ocr_engine', self.engine)
                    self.languages = config.get('languages', self.languages)
    
    def _initialize_reader(self) -> None:
        """Initialise le lecteur OCR en fonction du moteur choisi."""
        if self.engine == "easyocr":
            try:
                import easyocr
                self.reader = easyocr.Reader(self.languages, gpu=False)
            except ImportError:
                raise ImportError(
                    "EasyOCR n'est pas installé. Installez-le avec : pip install easyocr"
                )
        elif self.engine == "tesseract":
            try:
                import pytesseract
                from pytesseract import pytesseract as pt
                self.reader = pt
                # Vérifier que Tesseract est installé
                try:
                    pytesseract.get_tesseract_version()
                except EnvironmentError:
                    raise EnvironmentError(
                        "Tesseract OCR n'est pas installé. "
                        "Installez-le avec : sudo apt install tesseract-ocr (Linux) "
                        "ou via le site officiel pour Windows/macOS."
                    )
            except ImportError:
                raise ImportError(
                    "PyTesseract n'est pas installé. Installez-le avec : pip install pytesseract"
                )
        else:
            raise ValueError(f"Moteur OCR non supporté : {self.engine}")
    
    def preprocess_image(self, image_path: Union[str, Path]) -> np.ndarray:
        """
        Prétraite une image pour améliorer la reconnaissance OCR.
        
        Args:
            image_path: Chemin vers l'image à traiter.
            
        Returns:
            Image prétraitée sous forme de tableau NumPy.
        """
        # Charger l'image
        image = cv2.imread(str(image_path))
        if image is None:
            raise FileNotFoundError(f"Impossible de charger l'image : {image_path}")
        
        # Convertir en niveaux de gris
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Appliquer un seuil adaptatif
        thresh = cv2.adaptiveThreshold(
            gray, 255, 
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY_INV, 
            11, 2
        )
        
        # Supprimer le bruit
        kernel = np.ones((2, 2), np.uint8)
        processed = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=1)
        
        return processed
    
    def recognize_text(self, image_path: Union[str, Path], preprocess: bool = True) -> List[Dict[str, Union[str, float]]]:
        """
        Reconnaît le texte dans une image.
        
        Args:
            image_path: Chemin vers l'image à analyser.
            preprocess: Si True, prétraite l'image avant la reconnaissance.
            
        Returns:
            Liste de dictionnaires contenant le texte reconnu et sa confiance.
            Exemple : [{"text": "Bonjour", "confidence": 0.95}, ...]
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Fichier introuvable : {image_path}")
        
        if preprocess:
            processed_image = self.preprocess_image(image_path)
        else:
            processed_image = cv2.imread(str(image_path))
        
        if self.engine == "easyocr":
            results = self.reader.readtext(str(image_path))
            return [
                {"text": detection[1], "confidence": detection[2]}
                for detection in results
            ]
        elif self.engine == "tesseract":
            import pytesseract
            # Utiliser l'image prétraitée pour Tesseract
            text = pytesseract.image_to_string(processed_image, lang=",".join(self.languages))
            # Retourner un seul résultat avec une confiance estimée
            return [{"text": text.strip(), "confidence": 0.85}]
        else:
            raise ValueError(f"Moteur OCR non supporté : {self.engine}")
    
    def recognize_handwriting(self, image_path: Union[str, Path]) -> str:
        """
        Spécialisé pour la reconnaissance d'écriture manuscrite.
        Utilise EasyOCR avec des paramètres optimisés pour le manuscrit.
        
        Args:
            image_path: Chemin vers l'image de l'écriture manuscrite.
            
        Returns:
            Texte reconnu sous forme de chaîne de caractères.
        """
        if self.engine != "easyocr":
            print("⚠️ Warning: EasyOCR est recommandé pour l'écriture manuscrite. Utilisation de Tesseract peut donner de moins bons résultats.")
        
        results = self.recognize_text(image_path, preprocess=True)
        # Combiner tous les résultats en un seul texte
        recognized_text = " ".join([result["text"] for result in results])
        return recognized_text
    
    def batch_recognize(self, image_paths: List[Union[str, Path]]) -> Dict[str, str]:
        """
        Reconnaît le texte dans plusieurs images.
        
        Args:
            image_paths: Liste de chemins vers les images.
            
        Returns:
            Dictionnaire avec les chemins des images comme clés et le texte reconnu comme valeurs.
        """
        return {
            str(path): self.recognize_handwriting(path)
            for path in image_paths
        }
    
    def close(self) -> None:
        """Ferme les ressources du lecteur OCR."""
        if self.engine == "easyocr" and hasattr(self.reader, 'close'):
            self.reader.close()


# Exemple d'utilisation
if __name__ == "__main__":
    # Initialiser le moteur OCR
    ocr = OCREngine(engine="easyocr", languages=["fr"])
    
    # Exemple avec une image de test
    try:
        text = ocr.recognize_handwriting("examples/test1.png")
        print(f"Texte reconnu : {text}")
    except Exception as e:
        print(f"Erreur : {e}")
    finally:
        ocr.close()
