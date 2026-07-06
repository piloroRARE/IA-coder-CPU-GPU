#!/usr/bin/env python3
"""
Interface web pour le module OCR d'écriture manuscrite.

Utilise Flask pour créer une API REST et une interface utilisateur.
"""

import os
from flask import Flask, request, jsonify, render_template, send_file, redirect, url_for
from werkzeug.utils import secure_filename
from pathlib import Path
from typing import Optional, Union
import yaml

# Importer les modules locaux
from .ocr_engine import OCREngine
from .post_processing import PostProcessor
from .printer import TextPrinter


# Initialiser Flask
app = Flask(__name__)

# Configuration
app.config['UPLOAD_FOLDER'] = 'ocr_handwriting/examples'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff'}
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 Mo max

# Charger la configuration YAML
CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'config.yaml')
with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

# Initialiser les modules
ocr_engine = OCREngine(
    engine=config.get('ocr_engine', 'easyocr'),
    languages=config.get('languages', ['fr', 'en']),
    config_path=CONFIG_PATH
)

post_processor = PostProcessor(
    language=config.get('post_processing', {}).get('language', 'fr')
)

text_printer = TextPrinter(
    default_printer=config.get('printing', {}).get('default_printer')
)


def allowed_file(filename: str) -> bool:
    """Vérifie si le fichier a une extension autorisée."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


def ensure_upload_folder() -> None:
    """S'assure que le dossier de téléchargement existe."""
    upload_folder = Path(app.config['UPLOAD_FOLDER'])
    upload_folder.mkdir(parents=True, exist_ok=True)


@app.route('/')
def index():
    """Page d'accueil."""
    return render_template('index.html')


@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    """Gère le téléchargement et la reconnaissance d'images."""
    if request.method == 'POST':
        # Vérifier si le fichier est présent
        if 'file' not in request.files:
            return jsonify({'error': 'Aucun fichier sélectionné'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'Aucun fichier sélectionné'}), 400
        
        if file and allowed_file(file.filename):
            # Sécuriser le nom du fichier
            filename = secure_filename(file.filename)
            
            # Sauvegarder le fichier
            ensure_upload_folder()
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Reconnaître le texte
            try:
                raw_text = ocr_engine.recognize_handwriting(filepath)
                processed_text = post_processor.process(raw_text)
                
                return jsonify({
                    'filename': filename,
                    'raw_text': raw_text,
                    'processed_text': processed_text,
                    'message': 'Fichier téléchargé et texte reconnu avec succès'
                })
            except Exception as e:
                return jsonify({'error': f'Erreur lors de la reconnaissance OCR: {str(e)}'}), 500
        else:
            return jsonify({'error': 'Type de fichier non autorisé'}), 400
    
    return render_template('upload.html')


@app.route('/recognize', methods=['POST'])
def recognize():
    """API pour reconnaître du texte dans une image."""
    data = request.get_json()
    
    if not data or 'image_path' not in data:
        return jsonify({'error': 'Aucun chemin d\'image fourni'}), 400
    
    image_path = data['image_path']
    
    if not os.path.exists(image_path):
        return jsonify({'error': f'Fichier introuvable: {image_path}'}), 404
    
    try:
        raw_text = ocr_engine.recognize_handwriting(image_path)
        processed_text = post_processor.process(raw_text)
        
        return jsonify({
            'image_path': image_path,
            'raw_text': raw_text,
            'processed_text': processed_text
        })
    except Exception as e:
        return jsonify({'error': f'Erreur lors de la reconnaissance: {str(e)}'}), 500


@app.route('/process_text', methods=['POST'])
def process_text():
    """API pour traiter du texte brut."""
    data = request.get_json()
    
    if not data or 'text' not in data:
        return jsonify({'error': 'Aucun texte fourni'}), 400
    
    text = data['text']
    language = data.get('language', 'fr')
    
    try:
        processor = PostProcessor(language=language)
        processed_text = processor.process(text)
        
        return jsonify({
            'original_text': text,
            'processed_text': processed_text,
            'language': language
        })
    except Exception as e:
        return jsonify({'error': f'Erreur lors du traitement: {str(e)}'}), 500


@app.route('/print', methods=['POST'])
def print_text():
    """API pour imprimer du texte."""
    data = request.get_json()
    
    if not data or 'text' not in data:
        return jsonify({'error': 'Aucun texte fourni'}), 400
    
    text = data['text']
    format = data.get('format', 'txt')
    output_path = data.get('output_path')
    printer_name = data.get('printer_name')
    
    try:
        if format == 'print':
            # Impression directe
            success = text_printer.print_text(text, printer_name=printer_name)
            if success:
                return jsonify({'message': 'Impression réussie'})
            else:
                return jsonify({'error': 'Échec de l\'impression'}), 500
        else:
            # Sauvegarder dans un fichier
            file_path = text_printer.print_to_file(text, output_path, format)
            if file_path:
                return jsonify({
                    'message': f'Fichier généré: {file_path}',
                    'file_path': file_path
                })
            else:
                return jsonify({'error': 'Échec de la génération du fichier'}), 500
    except Exception as e:
        return jsonify({'error': f'Erreur lors de l\'impression: {str(e)}'}), 500


@app.route('/download/<filename>')
def download_file(filename: str):
    """Télécharger un fichier généré."""
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    if not os.path.exists(filepath):
        return jsonify({'error': 'Fichier introuvable'}), 404
    
    return send_file(filepath, as_attachment=True)


@app.route('/batch_recognize', methods=['POST'])
def batch_recognize():
    """API pour reconnaître du texte dans plusieurs images."""
    data = request.get_json()
    
    if not data or 'image_paths' not in data:
        return jsonify({'error': 'Aucun chemin d\'images fourni'}), 400
    
    image_paths = data['image_paths']
    
    try:
        results = ocr_engine.batch_recognize(image_paths)
        processed_results = {}
        
        for path, text in results.items():
            processed_results[path] = post_processor.process(text)
        
        return jsonify({
            'results': processed_results
        })
    except Exception as e:
        return jsonify({'error': f'Erreur lors de la reconnaissance par lots: {str(e)}'}), 500


@app.route('/config', methods=['GET'])
def get_config():
    """Récupère la configuration actuelle."""
    return jsonify(config)


@app.route('/health', methods=['GET'])
def health_check():
    """Vérifie l'état de l'API."""
    return jsonify({
        'status': 'healthy',
        'ocr_engine': ocr_engine.engine,
        'languages': ocr_engine.languages,
        'post_processor_language': post_processor.language
    })


# Créer le dossier des templates
TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), 'templates')
Path(TEMPLATES_DIR).mkdir(parents=True, exist_ok=True)

# Créer les templates HTML
@app.before_first_request
def create_templates():
    """Crée les templates HTML si ils n'existent pas."""
    index_template = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OCR Écriture Manuscrite</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        h1 {
            color: #333;
            text-align: center;
        }
        .container {
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .btn {
            background-color: #4CAF50;
            color: white;
            padding: 10px 15px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
            margin: 5px;
        }
        .btn:hover {
            background-color: #45a049;
        }
        .result {
            margin-top: 20px;
            padding: 15px;
            background-color: #f9f9f9;
            border-radius: 4px;
            white-space: pre-wrap;
        }
        .error {
            color: red;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📝 OCR Écriture Manuscrite</h1>
        <p>Téléchargez une image d'écriture manuscrite pour la reconnaître et l'imprimer.</p>
        
        <form action="/upload" method="post" enctype="multipart/form-data">
            <input type="file" name="file" accept="image/*" required>
            <button type="submit" class="btn">Reconnaître le texte</button>
        </form>
        
        <div id="result" class="result" style="display: none;"></div>
        
        <div id="error" class="error"></div>
    </div>
    
    <script>
        // Gérer la réponse de l'upload
        document.querySelector('form').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const formData = new FormData(e.target);
            const resultDiv = document.getElementById('result');
            const errorDiv = document.getElementById('error');
            
            resultDiv.style.display = 'none';
            errorDiv.textContent = '';
            
            try {
                const response = await fetch('/upload', {
                    method: 'POST',
                    body: formData
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    resultDiv.innerHTML = `
                        <h3>Résultat:</h3>
                        <p><strong>Fichier:</strong> ${data.filename}</p>
                        <p><strong>Texte brut:</strong> ${data.raw_text}</p>
                        <p><strong>Texte traité:</strong> ${data.processed_text}</p>
                        <button onclick="printText('${data.processed_text.replace(/'/g, "\\'")}')" class="btn">Imprimer</button>
                        <button onclick="saveAsFile('${data.processed_text.replace(/'/g, "\\'")}')" class="btn">Enregistrer</button>
                    `;
                    resultDiv.style.display = 'block';
                } else {
                    errorDiv.textContent = data.error || 'Erreur inconnue';
                }
            } catch (err) {
                errorDiv.textContent = 'Erreur de connexion: ' + err.message;
            }
        });
        
        function printText(text) {
            fetch('/print', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({text: text, format: 'print'})
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    alert('Erreur: ' + data.error);
                } else {
                    alert('Impression envoyée avec succès!');
                }
            })
            .catch(err => alert('Erreur: ' + err.message));
        }
        
        function saveAsFile(text) {
            const filename = prompt('Nom du fichier (sans extension):', 'ocr_output');
            if (!filename) return;
            
            fetch('/print', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({text: text, format: 'txt', output_path: filename + '.txt'})
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    alert('Erreur: ' + data.error);
                } else {
                    alert('Fichier enregistré: ' + data.file_path);
                }
            })
            .catch(err => alert('Erreur: ' + err.message));
        }
    </script>
</body>
</html>
"""
    
    upload_template = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Télécharger une image</title>
</head>
<body>
    <h1>Télécharger une image</h1>
    <form method="post" enctype="multipart/form-data">
        <input type="file" name="file">
        <button type="submit">Télécharger</button>
    </form>
</body>
</html>
"""
    
    with open(os.path.join(TEMPLATES_DIR, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(index_template)
    
    with open(os.path.join(TEMPLATES_DIR, 'upload.html'), 'w', encoding='utf-8') as f:
        f.write(upload_template)


# Fermer le moteur OCR lors de la fermeture de l'application
@app.teardown_appcontext
def close_ocr_engine(exception=None):
    """Ferme le moteur OCR lors de la fermeture de l'application."""
    ocr_engine.close()


if __name__ == '__main__':
    # Créer le dossier de téléchargement
    ensure_upload_folder()
    
    # Lancer l'application Flask
    app.run(host='0.0.0.0', port=5000, debug=True)
