# 📝 Module OCR pour l'Écriture Manuscrite

> **Projet** : Module de reconnaissance optique de caractères (OCR) spécialisé dans l'écriture manuscrite.
> **Intégration** : Fait partie du projet **IA-coder-CPU-GPU**.

---

## 🎯 **Fonctionnalités**

- ✅ **Reconnaissance d'écriture manuscrite** : Utilise **EasyOCR** (optimisé pour le manuscrit) ou **Tesseract** (pour le texte imprimé).
- ✅ **Prétraitement d'images** : Améliore la qualité des images avant reconnaissance (seuillage adaptatif, suppression du bruit).
- ✅ **Post-traitement du texte** : Nettoyage, correction des erreurs OCR, structuration du texte.
- ✅ **Impression** : Impression directe sur une imprimante locale ou génération de fichiers **PDF/texte**.
- ✅ **API REST** : Interface web avec **Flask** pour une intégration facile.
- ✅ **Interface utilisateur** : Page web simple pour télécharger des images et voir les résultats.

---

## 🏗 **Architecture**

```
ocr_handwriting/
├── __init__.py           # Module principal
├── ocr_engine.py         # Moteur OCR (EasyOCR/Tesseract)
├── post_processing.py    # Nettoyage et correction du texte
├── printer.py            # Module d'impression (PDF, texte, imprimante)
├── app.py                # Interface web (Flask)
├── config.yaml           # Configuration
├── requirements.txt      # Dépendances Python
├── templates/            # Templates HTML (générés automatiquement)
│   ├── index.html        # Page principale
│   └── upload.html       # Page de téléchargement
└── examples/             # Exemples d'images manuscrites
    ├── test1.png
    └── test2.jpg
```

---

## 🚀 **Installation**

### 1. **Cloner le dépôt**
```bash
cd IA-coder-CPU-GPU
git pull origin main
```

### 2. **Installer les dépendances**

#### **Option 1 : Installer uniquement les dépendances du module OCR**
```bash
pip install -r ocr_handwriting/requirements.txt
```

#### **Option 2 : Installer toutes les dépendances (y compris celles du projet principal)**
```bash
pip install -r requirements.txt
pip install -r ocr_handwriting/requirements.txt
```

### 3. **Installer Tesseract OCR (optionnel)**

Si vous souhaitez utiliser **Tesseract** comme moteur OCR :

- **Linux (Debian/Ubuntu)** :
  ```bash
  sudo apt update
  sudo apt install tesseract-ocr
  sudo apt install libtesseract-dev
  sudo apt install tesseract-ocr-fra  # Pour le français
  sudo apt install tesseract-ocr-eng  # Pour l'anglais
  ```

- **macOS** :
  ```bash
  brew install tesseract
  brew install tesseract-lang  # Pour les langues supplémentaires
  ```

- **Windows** :
  Téléchargez et installez depuis [le site officiel de Tesseract](https://github.com/UB-Mannheim/tesseract/wiki).

### 4. **Installer EasyOCR**

EasyOCR est inclus dans `requirements.txt` et sera installé automatiquement avec `pip`.

> **⚠️ Note** : EasyOCR télécharge automatiquement les modèles de langues lors de la première utilisation.

---

## 🔧 **Utilisation**

### **1. Utilisation en ligne de commande**

#### **Reconnaître du texte dans une image**
```python
from ocr_handwriting.ocr_engine import OCREngine
from ocr_handwriting.post_processing import PostProcessor

# Initialiser le moteur OCR
ocr = OCREngine(engine="easyocr", languages=["fr"])

# Reconnaître le texte dans une image
raw_text = ocr.recognize_handwriting("examples/test1.png")
print(f"Texte brut : {raw_text}")

# Nettoyer et structurer le texte
processor = PostProcessor(language="fr")
cleaned_text = processor.process(raw_text)
print(f"Texte traité : {cleaned_text}")

# Fermer le moteur OCR
ocr.close()
```

#### **Imprimer ou enregistrer le texte**
```python
from ocr_handwriting.printer import TextPrinter

printer = TextPrinter()

# Enregistrer en PDF
pdf_path = printer.save_as_pdf(cleaned_text, title="Mon Document")
print(f"PDF généré : {pdf_path}")

# Enregistrer en texte
txt_path = printer.save_as_txt(cleaned_text, output_path="output.txt")
print(f"Fichier texte généré : {txt_path}")

# Imprimer directement (nécessite une imprimante configurée)
success = printer.print_text(cleaned_text)
if success:
    print("Impression réussie !")
```

### **2. Utilisation de l'API REST**

#### **Lancer le serveur Flask**
```bash
cd IA-coder-CPU-GPU
python -m ocr_handwriting.app
```

Le serveur sera accessible à l'adresse : [http://localhost:5000](http://localhost:5000)

#### **Endpoints disponibles**

| **Endpoint**          | **Méthode** | **Description**                                                                 | **Exemple de requête**                                                                 |
|-----------------------|-------------|---------------------------------------------------------------------------------|--------------------------------------------------------------------------------------|
| `/`                   | GET         | Page d'accueil avec interface utilisateur.                                       | [http://localhost:5000](http://localhost:5000)                                    |
| `/upload`             | POST        | Télécharger une image et reconnaître le texte.                                   | `curl -X POST -F "file=@test.png" http://localhost:5000/upload`                     |
| `/recognize`          | POST        | Reconnaître du texte dans une image (chemin spécifié).                          | `curl -X POST -H "Content-Type: application/json" -d '{"image_path":"test.png"}' http://localhost:5000/recognize` |
| `/process_text`       | POST        | Traiter du texte brut (nettoyage, correction).                                   | `curl -X POST -H "Content-Type: application/json" -d '{"text":"Bonjour 0n a1me"}' http://localhost:5000/process_text` |
| `/print`              | POST        | Imprimer du texte (directement ou dans un fichier).                            | `curl -X POST -H "Content-Type: application/json" -d '{"text":"Bonjour","format":"pdf"}' http://localhost:5000/print` |
| `/batch_recognize`    | POST        | Reconnaître du texte dans plusieurs images.                                    | `curl -X POST -H "Content-Type: application/json" -d '{"image_paths":["test1.png","test2.png"]}' http://localhost:5000/batch_recognize` |
| `/config`             | GET         | Récupérer la configuration actuelle.                                           | `curl http://localhost:5000/config`                                                |
| `/health`             | GET         | Vérifier l'état de l'API.                                                        | `curl http://localhost:5000/health`                                              |
| `/download/<filename>`| GET         | Télécharger un fichier généré.                                                  | `curl http://localhost:5000/download/output.txt`                                |

---

## 📂 **Exemples d'Images**

Placez vos images d'écriture manuscrite dans le dossier `ocr_handwriting/examples/`.

Exemples de formats supportés :
- `.png`
- `.jpg` / `.jpeg`
- `.gif`
- `.bmp`
- `.tiff`

---

## 🎛 **Configuration**

Le fichier `config.yaml` permet de personnaliser le comportement du module OCR :

```yaml
# Moteur OCR à utiliser
ocr_engine: "easyocr"  # ou "tesseract"

# Langues supportées
languages: ["fr", "en"]

# Paramètres de prétraitement
preprocessing:
  adaptive_threshold: true
  kernel_size: [2, 2]
  morph_iterations: 1

# Paramètres de post-traitement
post_processing:
  language: "fr"
  correct_errors: true
  structure_text: true

# Paramètres d'impression
printing:
  default_printer: null
  default_copies: 1
  default_format: "txt"
```

---

## 🤖 **Modèles Utilisés**

| **Moteur**  | **Modèle**               | **Tâche**                          | **Langues**               | **Précision** |
|-------------|--------------------------|------------------------------------|---------------------------|---------------|
| EasyOCR     | Modèles pré-entraînés    | Reconnaissance d'écriture manuscrite | fr, en, es, de, etc.      | ⭐⭐⭐⭐⭐      |
| Tesseract   | Modèles standard         | Reconnaissance de texte imprimé    | fr, en, es, de, etc.      | ⭐⭐⭐⭐        |

---

## 📊 **Performances**

| **Métrique**               | **EasyOCR** | **Tesseract** |
|----------------------------|-------------|---------------|
| Temps de reconnaissance     | ~1-2 sec    | ~0.5-1 sec    |
| Précision (manuscrit)      | ⭐⭐⭐⭐⭐      | ⭐⭐           |
| Précision (imprimé)        | ⭐⭐⭐⭐        | ⭐⭐⭐⭐⭐      |
| Support multi-langues       | ✅ Oui       | ✅ Oui        |
| Nécessite un GPU            | ❌ Non       | ❌ Non        |

---

## 🔄 **Intégration avec le Projet Principal**

Ce module peut être intégré dans le système **IA-coder-CPU-GPU** comme une **IA faible spécialisée** :

```python
from ocr_handwriting.ocr_engine import OCREngine
from ocr_handwriting.post_processing import PostProcessor
from ocr_handwriting.printer import TextPrinter

class HandwritingOCR:
    """IA faible spécialisée dans la reconnaissance d'écriture manuscrite."""
    
    def __init__(self):
        self.ocr_engine = OCREngine(engine="easyocr", languages=["fr"])
        self.post_processor = PostProcessor(language="fr")
        self.printer = TextPrinter()
    
    def recognize_and_print(self, image_path: str, output_format: str = "txt") -> str:
        """
        Reconnaît le texte dans une image et l'imprime/enregistre.
        
        Args:
            image_path: Chemin vers l'image.
            output_format: Format de sortie ('txt', 'pdf', 'print').
            
        Returns:
            Chemin vers le fichier généré ou message de succès.
        """
        # Reconnaître le texte
        raw_text = self.ocr_engine.recognize_handwriting(image_path)
        
        # Traiter le texte
        processed_text = self.post_processor.process(raw_text)
        
        # Imprimer/enregistrer
        if output_format == "print":
            success = self.printer.print_text(processed_text)
            return "Impression réussie" if success else "Échec de l'impression"
        else:
            file_path = self.printer.print_to_file(processed_text, format=output_format)
            return file_path
    
    def close(self):
        """Ferme les ressources."""
        self.ocr_engine.close()
```

---

## 📜 **Licence**

Ce module est sous licence **MIT**, comme le projet principal **IA-coder-CPU-GPU**. Vous êtes libre de l'utiliser, le modifier et le distribuer.

---

## 🙌 **Contribuer**

Les contributions sont les bienvenues ! Voici comment contribuer :

1. **Fork** le dépôt.
2. Créez une **branche** pour votre fonctionnalité (`git checkout -b feature/ocr-improvements`).
3. **Commit** vos changements (`git commit -m "Ajout de la fonctionnalité X"`).
4. **Push** vers la branche (`git push origin feature/ocr-improvements`).
5. Ouvrez une **Pull Request**.

---

## 📞 **Support**

Pour toute question ou suggestion, contactez-moi via [GitHub](https://github.com/piloroRARE).

---

## 📚 **Ressources**

- [Documentation EasyOCR](https://github.com/JaidedAI/EasyOCR)
- [Documentation Tesseract](https://github.com/tesseract-ocr/tesseract)
- [Documentation Flask](https://flask.palletsprojects.com/)
- [Documentation OpenCV](https://docs.opencv.org/)
