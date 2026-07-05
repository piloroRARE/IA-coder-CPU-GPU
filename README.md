# IA Forte pour Python (CPU-GPU)

> **Projet** : Créer une IA forte à partir de plusieurs IA faibles spécialisées dans des tâches spécifiques (ex: génération de code, correction, analyse). Une IA tuteur décide laquelle utiliser.

> **Environnement** : Compatible **CPU uniquement** (optimisé pour les machines sans GPU).

---

## 📌 Table des Matières
- [🎯 Objectif](#-objectif)
- [🏗 Architecture](#-architecture)
- [📁 Structure du Projet](#-structure-du-projet)
- [🚀 Installation](#-installation)
- [🔧 Utilisation](#-utilisation)
- [📂 Dossiers et Fichiers](#-dossiers-et-fichiers)
- [🤖 Modèles Utilisés](#-modèles-utilisés)
- [🌐 Interface Web](#-interface-web)
- [📜 Licence](#-licence)

---

## 🎯 Objectif
Créer un système d'**IA forte** capable de :
1. **Générer du code Python** à partir de descriptions en français.
2. **Corriger des bugs** dans du code existant.
3. **Analyser la complexité** d'un algorithme.
4. **Sélectionner automatiquement** la bonne IA en fonction de la tâche demandée.

---

## 🏗 Architecture
```
IA-coder-CPU-GPU/
├── scripts/                  # Scripts Python pour l'entraînement et la conversion
│   ├── train_code_generator.py   # Entraînement du générateur de code
│   └── convert_to_onnx.py        # Conversion des modèles en ONNX
├── models/                   # Modèles entraînés (exclus de Git)
│   └── code_generator/           # Modèle de génération de code
├── web/                      # Interface web
│   ├── index.html               # Page principale
│   ├── js/                     # Scripts JavaScript
│   │   └── orchestrator.js      # Orchestrateur (IA tuteur)
│   ├── tfjs_models/            # Modèles TensorFlow.js
│   └── onnx_models/            # Modèles ONNX
├── data/                     # Datasets (exclus de Git)
├── requirements.txt           # Dépendances Python
├── .gitignore                # Fichiers à ignorer
└── README.md                  # Documentation
```

---

## 📁 Structure du Projet
| **Dossier**       | **Description**                                                                 |
|-------------------|---------------------------------------------------------------------------------|
| `scripts/`        | Contient les scripts Python pour l'entraînement et la conversion des modèles.   |
| `models/`         | Stocke les modèles entraînés (ex: `code_generator/`, `code_fixer/`).            |
| `web/`            | Contient l'interface web et les modèles convertis pour le navigateur.          |
| `web/js/`         | Scripts JavaScript (ex: orchestrateur, gestion des modèles).                   |
| `web/tfjs_models/`| Modèles convertis en TensorFlow.js pour une utilisation dans le navigateur.     |
| `web/onnx_models/`| Modèles convertis en ONNX pour une utilisation avec ONNX.js.                  |
| `data/`           | Datasets utilisés pour l'entraînement (exclus de Git).                          |

---

## 🚀 Installation
### 1. Cloner le dépôt
```bash
git clone https://github.com/piloroRARE/IA-coder-CPU-GPU.git
cd IA-coder-CPU-GPU
```

### 2. Installer les dépendances
```bash
pip install -r requirements.txt
```

> **⚠️ Note** : Certaines dépendances (comme `bitsandbytes`) peuvent nécessiter des installations supplémentaires sur certains systèmes. Consultez la [documentation officielle](https://github.com/TimDettmers/bitsandbytes) si nécessaire.

---

## 🔧 Utilisation
### 1. Entraîner un modèle
Pour entraîner le **générateur de code** :
```bash
python scripts/train_code_generator.py
```
> **⏳ Temps estimé** : 30-60 minutes sur CPU (selon la puissance de votre machine).

### 2. Convertir un modèle en ONNX
```bash
python scripts/convert_to_onnx.py
```
> **✅ Sortie** : Fichier `.onnx` dans `web/onnx_models/`.

### 3. Lancer l'interface web
```bash
cd web
python -m http.server 8000
```
> **🌐 Accès** : Ouvrez [http://localhost:8000](http://localhost:8000) dans votre navigateur.

---

## 📂 Dossiers et Fichiers
| **Fichier**                     | **Description**                                                                 |
|--------------------------------|---------------------------------------------------------------------------------|
| `scripts/train_code_generator.py` | Script pour entraîner le générateur de code avec TinyLlama + LoRA.            |
| `scripts/convert_to_onnx.py`     | Script pour convertir les modèles PyTorch en ONNX.                            |
| `web/index.html`                | Interface web pour interagir avec les IA.                                      |
| `web/js/orchestrator.js`       | Orchestrateur (IA tuteur) qui sélectionne la bonne IA.                         |
| `requirements.txt`              | Liste des dépendances Python.                                                  |
| `.gitignore`                   | Fichiers à exclure de Git (modèles, datasets, etc.).                            |

---

## 🤖 Modèles Utilisés
| **IA Faible**               | **Modèle**               | **Tâche**                          | **Taille** | **Framework**       |
|-----------------------------|--------------------------|------------------------------------|------------|---------------------|
| Générateur de Code          | TinyLlama-1.1B + LoRA    | Générer du code Python.            | ~1.1B      | PyTorch/HuggingFace  |
| Correcteur de Code          | Phi-3-mini-4k-instruct   | Corriger des bugs.                 | ~3.8B      | PyTorch/HuggingFace  |
| Analyseur de Complexité     | DistilBERT (custom)      | Estimer la complexité (O(n), etc.).| ~66M       | TensorFlow          |

---

## 🌐 Interface Web
### Fonctionnalités
- **Saisie de requêtes** : Entrez une description en français (ex: "Écris une fonction pour calculer la factorielle").
- **Exemples prédéfinis** : Boutons pour charger des requêtes types.
- **Affichage du résultat** : Code Python généré ou corrigé.
- **Orchestrateur** : Sélection automatique de l'IA appropriée.

### Technologies Utilisées
- **TensorFlow.js** : Pour exécuter des modèles TensorFlow dans le navigateur.
- **ONNX.js** : Pour exécuter des modèles ONNX dans le navigateur.
- **HTML/CSS/JS** : Interface utilisateur moderne et responsive.

---

## 📜 Licence
Ce projet est sous licence **MIT**. Vous êtes libre de l'utiliser, le modifier et le distribuer.

---

## 🙌 Contribuer
Les contributions sont les bienvenues ! Ouvrez une **Pull Request** ou un **Issue** pour proposer des améliorations.

---

## 📞 Contact
Pour toute question ou suggestion, contactez-moi via [GitHub](https://github.com/piloroRARE).
