#!/usr/bin/env python3
"""
Module de post-traitement pour le texte reconnu par OCR.

Nettoie, structure et améliore le texte reconnu avant impression.
"""

import re
from typing import List, Dict, Optional, Union
from collections import Counter


class PostProcessor:
    """
    Classe pour le post-traitement du texte reconnu par OCR.
    
    Fonctionnalités :
    - Nettoyage du texte (suppression des caractères indésirables).
    - Correction des erreurs courantes (OCR).
    - Structuration du texte (paragraphes, listes, etc.).
    - Détection de la langue.
    """
    
    def __init__(self, language: str = "fr"):
        """
        Initialise le post-processeur.
        
        Args:
            language: Langue principale du texte (ex: 'fr', 'en').
        """
        self.language = language
        self._load_common_errors()
    
    def _load_common_errors(self) -> None:
        """Charge les erreurs OCR courantes pour la langue spécifiée."""
        # Dictionnaire des corrections pour le français
        self.common_errors = {
            "fr": {
                r"0": "o",  # 0 -> o (même au milieu des mots)
                r"1": "l",  # 1 -> l
                r"5": "s",  # 5 -> s
                r"8": "b",  # 8 -> b
                r"2": "z",  # 2 -> z
                r"4": "a",  # 4 -> a
                r"6": "g",  # 6 -> g
                r"9": "g",  # 9 -> g
                r"\|": "l", # | -> l
                r"@": "a",  # @ -> a
                r"\b#\b": "",   # # -> vide
                r"\b\$\b": "s", # $ -> s
                r"\b%\b": "",   # % -> vide
                r"\b&\b": "et", # & -> et
                r"\b\*\b": "",  # * -> vide
                r"\b\+\b": "",  # + -> vide
                r"\b=\b": "",   # = -> vide
                r"\b-\b": " ",  # - -> espace
                r"\b_\b": " ",  # _ -> espace
                r"\b\.\b": "",  # . -> vide (si isolé)
                r"\b,\b": "",   # , -> vide (si isolé)
                r"\b;\b": "",   # ; -> vide (si isolé)
                r"\b:\b": "",   # : -> vide (si isolé)
                r"\b!\b": "",   # ! -> vide (si isolé)
                r"\b\?\b": "",  # ? -> vide (si isolé)
                r"\b\"\b": "",  # " -> vide (si isolé)
                r"\b'\b": "",   # ' -> vide (si isolé)
                r"\b\(\b": "",  # ( -> vide (si isolé)
                r"\b\)\b": "",  # ) -> vide (si isolé)
                r"\b\[\b": "",  # [ -> vide (si isolé)
                r"\b\]\b": "",  # ] -> vide (si isolé)
                r"\b\{\b": "",  # { -> vide (si isolé)
                r"\b\}\b": "",  # } -> vide (si isolé)
                r"\b/\b": " ",  # / -> espace
                r"\b\\\b": " ", # \ -> espace
                r"\b\|\b": "l", # | -> l
                r"\b~\b": "",   # ~ -> vide
                r"\b`\b": "",   # ` -> vide
                r"\b<\b": "",   # < -> vide
                r"\b>\b": "",   # > -> vide
                # Corrections spécifiques pour le français
                r"\bce\b": "ce",
                r"\bse\b": "se",
                r"\bne\b": "ne",
                r"\bde\b": "de",
                r"\ble\b": "le",
                r"\bla\b": "la",
                r"\bje\b": "je",
                r"\bme\b": "me",
                r"\bte\b": "te",
                r"\bque\b": "que",
                r"\bqui\b": "qui",
                r"\bpas\b": "pas",
                r"\bplus\b": "plus",
                r"\bavec\b": "avec",
                r"\bpour\b": "pour",
                r"\bsur\b": "sur",
                r"\bpar\b": "par",
                r"\bun\b": "un",
                r"\bune\b": "une",
                r"\bdes\b": "des",
                r"\bles\b": "les",
                r"\bet\b": "et",
                r"\best\b": "est",
                r"\bson\b": "son",
                r"\bma\b": "ma",
                r"\bta\b": "ta",
                r"\bsa\b": "sa",
            },
            "en": {
                r"\b0\b": "o",
                r"\b1\b": "l",
                r"\b5\b": "s",
                r"\b8\b": "b",
                r"\b2\b": "z",
                r"\b4\b": "a",
                r"\b6\b": "g",
                r"\b9\b": "g",
                r"\b\|\b": "l",
                r"\b@\b": "a",
                r"\b#\b": "",
                r"\b\$\b": "s",
                r"\b%\b": "",
                r"\b&\b": "and",
                r"\b\*\b": "",
                r"\b\+\b": "",
                r"\b=\b": "",
                r"\b-\b": " ",
                r"\b_\b": " ",
            }
        }
        self.error_patterns = self.common_errors.get(self.language, {})
    
    def clean_text(self, text: str) -> str:
        """
        Nettoie le texte en supprimant les caractères indésirables.
        
        Args:
            text: Texte à nettoyer.
            
        Returns:
            Texte nettoyé.
        """
        if not text:
            return ""
        
        # Supprimer les espaces en trop
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Supprimer les sauts de ligne en trop
        text = re.sub(r'\n+', '\n', text)
        
        # Supprimer les tabulations
        text = text.replace('\t', ' ')
        
        # Appliquer les corrections courantes
        for pattern, replacement in self.error_patterns.items():
            text = re.sub(pattern, replacement, text)
        
        return text
    
    def correct_ocr_errors(self, text: str) -> str:
        """
        Corrige les erreurs courantes de reconnaissance OCR.
        
        Args:
            text: Texte à corriger.
            
        Returns:
            Texte corrigé.
        """
        # Remplacer les caractères souvent mal reconnus
        corrections = {
            "Ô": "O", "ô": "o",
            "À": "A", "à": "a",
            "È": "E", "è": "e",
            "É": "E", "é": "e",
            "Ê": "E", "ê": "e",
            "Ë": "E", "ë": "e",
            "Î": "I", "î": "i",
            "Ï": "I", "ï": "i",
            "Û": "U", "û": "u",
            "Ü": "U", "ü": "u",
            "Ç": "C", "ç": "c",
            "Ñ": "N", "ñ": "n",
            "«": "", "»": "",
            "“": "", "”": "",
            "‘": "", "’": "",
            "…": "...",
            "–": "-", "—": "-",
            "’": "'",
        }
        
        for wrong, correct in corrections.items():
            text = text.replace(wrong, correct)
        
        return text
    
    def structure_text(self, text: str) -> str:
        """
        Structure le texte (paragraphes, listes, etc.).
        
        Args:
            text: Texte à structurer.
            
        Returns:
            Texte structuré.
        """
        if not text:
            return ""
        
        # Ajouter des espaces après les ponctuations
        text = re.sub(r'([.,!?;:])([^\s])', r'\1 \2', text)
        
        # Structurer les listes
        text = re.sub(r'(\d+)\s*\.', r'\1. ', text)
        text = re.sub(r'(\d+)\s*\)', r'\1) ', text)
        text = re.sub(r'(\d+)\s*\-', r'\1- ', text)
        
        # Structurer les paragraphes
        text = re.sub(r'\n\s*\n', '\n\n', text)
        
        return text
    
    def detect_language(self, text: str) -> str:
        """
        Détecte la langue du texte (simplifié).
        
        Args:
            text: Texte à analyser.
            
        Returns:
            Langue détectée ('fr' ou 'en').
        """
        if not text:
            return "unknown"
        
        # Mots courants en français
        french_words = {"le", "la", "les", "de", "des", "un", "une", "et", "est", "en", "je", "me", "te", "se", "ne", "pas", "plus", "avec", "pour", "sur", "par", "ce", "cette", "ces", "qui", "que", "quoi", "où", "quand", "comment", "pourquoi"}
        
        # Mots courants en anglais
        english_words = {"the", "a", "an", "and", "is", "are", "in", "on", "at", "to", "of", "for", "with", "this", "that", "these", "those", "it", "its", "my", "your", "his", "her", "our", "their"}
        
        # Compter les mots
        words = re.findall(r'\b\w+\b', text.lower())
        french_count = sum(1 for word in words if word in french_words)
        english_count = sum(1 for word in words if word in english_words)
        
        if french_count > english_count:
            return "fr"
        elif english_count > french_count:
            return "en"
        else:
            return "unknown"
    
    def process(self, text: str, clean: bool = True, correct: bool = True, structure: bool = True) -> str:
        """
        Traite le texte avec toutes les étapes de post-traitement.
        
        Args:
            text: Texte à traiter.
            clean: Si True, nettoie le texte.
            correct: Si True, corrige les erreurs OCR.
            structure: Si True, structure le texte.
            
        Returns:
            Texte traité.
        """
        if clean:
            text = self.clean_text(text)
        if correct:
            text = self.correct_ocr_errors(text)
        if structure:
            text = self.structure_text(text)
        
        return text
    
    def batch_process(self, texts: List[str]) -> List[str]:
        """
        Traite une liste de textes.
        
        Args:
            texts: Liste de textes à traiter.
            
        Returns:
            Liste de textes traités.
        """
        return [self.process(text) for text in texts]


# Exemple d'utilisation
if __name__ == "__main__":
    processor = PostProcessor(language="fr")
    
    # Exemple de texte brut
    raw_text = "Bonjour, je m'appelle Jean. J'ai 25 ans et j'habite à Paris. 0n a1me le café!"
    
    # Traiter le texte
    cleaned_text = processor.process(raw_text)
    print(f"Texte original : {raw_text}")
    print(f"Texte traité : {cleaned_text}")
