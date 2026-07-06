#!/usr/bin/env python3
"""
Module d'impression pour le texte reconnu par OCR.

Permet d'imprimer le texte sur une imprimante locale ou de générer un fichier PDF/texte.
"""

import os
import tempfile
from typing import Optional, Union
from pathlib import Path
from datetime import datetime


class TextPrinter:
    """
    Classe pour l'impression du texte reconnu.
    
    Fonctionnalités :
    - Impression directe sur une imprimante locale.
    - Génération de fichiers PDF.
    - Génération de fichiers texte.
    - Aperçu avant impression.
    """
    
    def __init__(self, default_printer: Optional[str] = None):
        """
        Initialise l'imprimeur de texte.
        
        Args:
            default_printer: Nom de l'imprimante par défaut (None pour utiliser la valeur par défaut du système).
        """
        self.default_printer = default_printer
        self._check_dependencies()
    
    def _check_dependencies(self) -> None:
        """Vérifie que les dépendances nécessaires sont installées."""
        try:
            import cups
            self.cups_available = True
        except ImportError:
            self.cups_available = False
            print("⚠️ Warning: La bibliothèque 'cups' n'est pas installée. L'impression directe ne sera pas disponible.")
        
        try:
            from fpdf import FPDF
            self.fpdf_available = True
        except ImportError:
            self.fpdf_available = False
            print("⚠️ Warning: La bibliothèque 'fpdf' n'est pas installée. La génération de PDF ne sera pas disponible.")
    
    def print_text(self, text: str, printer_name: Optional[str] = None, copies: int = 1) -> bool:
        """
        Imprime directement le texte sur une imprimante.
        
        Args:
            text: Texte à imprimer.
            printer_name: Nom de l'imprimante (None pour utiliser la valeur par défaut).
            copies: Nombre de copies à imprimer.
            
        Returns:
            True si l'impression a réussi, False sinon.
        """
        if not text:
            print("❌ Erreur: Aucun texte à imprimer.")
            return False
        
        if not self.cups_available:
            print("❌ Erreur: La bibliothèque 'cups' n'est pas disponible. Utilisez une autre méthode d'impression.")
            return False
        
        try:
            import cups
            
            # Créer un fichier temporaire
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                f.write(text)
                temp_file = f.name
            
            # Configurer l'impression
            conn = cups.Connection()
            printers = conn.getPrinters()
            
            if not printers:
                print("❌ Erreur: Aucune imprimante trouvée.")
                return False
            
            # Utiliser l'imprimante spécifiée ou la première disponible
            printer = printer_name or self.default_printer or list(printers.keys())[0]
            
            # Imprimer le fichier
            conn.printFile(printer, temp_file, "OCR Output", {"copies": str(copies)})
            
            # Supprimer le fichier temporaire
            os.unlink(temp_file)
            
            print(f"✅ Impression réussie sur {printer} ({copies} copie(s)).")
            return True
            
        except Exception as e:
            print(f"❌ Erreur lors de l'impression: {e}")
            return False
    
    def save_as_pdf(self, text: str, output_path: Optional[Union[str, Path]] = None, title: str = "OCR Output") -> Optional[str]:
        """
        Génère un fichier PDF avec le texte.
        
        Args:
            text: Texte à inclure dans le PDF.
            output_path: Chemin de sortie pour le PDF (None pour générer un nom automatique).
            title: Titre du document PDF.
            
        Returns:
            Chemin vers le fichier PDF généré, ou None en cas d'erreur.
        """
        if not text:
            print("❌ Erreur: Aucun texte à enregistrer.")
            return None
        
        if not self.fpdf_available:
            print("❌ Erreur: La bibliothèque 'fpdf' n'est pas disponible.")
            return None
        
        try:
            from fpdf import FPDF
            
            # Créer un nom de fichier par défaut
            if output_path is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = Path(f"ocr_output_{timestamp}.pdf")
            else:
                output_path = Path(output_path)
            
            # Créer le PDF
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            
            # Ajouter le titre
            pdf.set_font("Arial", 'B', 16)
            pdf.cell(0, 10, title, ln=True, align='C')
            pdf.ln(10)
            
            # Ajouter le texte
            pdf.set_font("Arial", size=12)
            pdf.multi_cell(0, 10, text)
            
            # Sauvegarder le PDF
            pdf.output(str(output_path))
            
            print(f"✅ PDF généré: {output_path}")
            return str(output_path)
            
        except Exception as e:
            print(f"❌ Erreur lors de la génération du PDF: {e}")
            return None
    
    def save_as_txt(self, text: str, output_path: Optional[Union[str, Path]] = None) -> Optional[str]:
        """
        Génère un fichier texte avec le texte reconnu.
        
        Args:
            text: Texte à enregistrer.
            output_path: Chemin de sortie pour le fichier texte (None pour générer un nom automatique).
            
        Returns:
            Chemin vers le fichier texte généré, ou None en cas d'erreur.
        """
        if not text:
            print("❌ Erreur: Aucun texte à enregistrer.")
            return None
        
        try:
            # Créer un nom de fichier par défaut
            if output_path is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = Path(f"ocr_output_{timestamp}.txt")
            else:
                output_path = Path(output_path)
            
            # Écrire le texte dans le fichier
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(text)
            
            print(f"✅ Fichier texte généré: {output_path}")
            return str(output_path)
            
        except Exception as e:
            print(f"❌ Erreur lors de l'enregistrement du fichier texte: {e}")
            return None
    
    def preview_text(self, text: str, max_lines: int = 20) -> str:
        """
        Affiche un aperçu du texte avant impression.
        
        Args:
            text: Texte à prévisualiser.
            max_lines: Nombre maximum de lignes à afficher.
            
        Returns:
            Aperçu du texte (tronqué si nécessaire).
        """
        if not text:
            return "Aucun texte à prévisualiser."
        
        lines = text.split('\n')
        if len(lines) > max_lines:
            preview = '\n'.join(lines[:max_lines]) + f"\n... ({len(lines) - max_lines} lignes supplémentaires)"
        else:
            preview = text
        
        return preview
    
    def print_to_file(self, text: str, output_path: Union[str, Path], format: str = "txt") -> Optional[str]:
        """
        Imprime le texte dans un fichier (PDF ou texte).
        
        Args:
            text: Texte à enregistrer.
            output_path: Chemin de sortie pour le fichier.
            format: Format du fichier ('txt' ou 'pdf').
            
        Returns:
            Chemin vers le fichier généré, ou None en cas d'erreur.
        """
        if format == "pdf":
            return self.save_as_pdf(text, output_path)
        elif format == "txt":
            return self.save_as_txt(text, output_path)
        else:
            print(f"❌ Erreur: Format non supporté: {format}")
            return None


# Exemple d'utilisation
if __name__ == "__main__":
    printer = TextPrinter()
    
    # Exemple de texte
    text = "Bonjour, ce texte sera imprimé ou enregistré dans un fichier."
    
    # Prévisualisation
    print("📄 Aperçu du texte:")
    print(printer.preview_text(text))
    
    # Sauvegarder en PDF
    pdf_path = printer.save_as_pdf(text, title="Test OCR")
    print(f"PDF généré: {pdf_path}")
    
    # Sauvegarder en texte
    txt_path = printer.save_as_txt(text)
    print(f"Fichier texte généré: {txt_path}")
