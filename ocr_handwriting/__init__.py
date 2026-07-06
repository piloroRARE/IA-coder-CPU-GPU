#!/usr/bin/env python3
"""
Module OCR pour la reconnaissance d'écriture manuscrite.

Ce module permet de :
- Reconnaître du texte manuscrit dans des images.
- Nettoyer et structurer le texte reconnu.
- Imprimer le texte reconnu.

Auteurs : IA-coder-CPU-GPU
Licence : MIT
"""

__version__ = "1.0.0"
__all__ = ["OCREngine", "PostProcessor", "TextPrinter"]

# Imports lazy pour éviter les erreurs si les dépendances ne sont pas installées
def __getattr__(name):
    if name == "OCREngine":
        from .ocr_engine import OCREngine
        return OCREngine
    elif name == "PostProcessor":
        from .post_processing import PostProcessor
        return PostProcessor
    elif name == "TextPrinter":
        from .printer import TextPrinter
        return TextPrinter
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
