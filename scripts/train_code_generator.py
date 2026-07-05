#!/usr/bin/env python3
"""
Script d'entraînement pour un générateur de code Python.
Utilise TinyLlama-1.1B avec LoRA et 8-bit quantization pour être compatible CPU.
"""

from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments
from peft import LoraConfig, get_peft_model
from datasets import load_dataset
import torch
import os

# Configuration des chemins
OUTPUT_DIR = "./models/code_generator"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Charger un sous-ensemble du dataset (1k exemples pour éviter les timeouts sur CPU)
print("⏳ Chargement du dataset...")
try:
    dataset = load_dataset("defog/python-code-instructions", split="train[:1000]")
    print(f"✅ Dataset chargé : {len(dataset)} exemples.")
except Exception as e:
    print(f"❌ Erreur lors du chargement du dataset : {e}")
    print("🔄 Tentative avec un dataset local ou plus petit...")
    # Créer un dataset de test si le téléchargement échoue
    from datasets import Dataset
    dataset = Dataset.from_dict({
        "instruction": [
            "Écris une fonction pour additionner deux nombres",
            "Écris une fonction pour calculer la factorielle",
            "Écris une fonction pour trier une liste"
        ],
        "code": [
            "def add(a, b):\n    return a + b",
            "def factorial(n):\n    if n == 0:\n        return 1\n    else:\n        return n * factorial(n-1)",
            "def sort_list(lst):\n    return sorted(lst)"
        ]
    })
    print(f"✅ Dataset de test créé : {len(dataset)} exemples.")

# Charger TinyLlama (modèle léger)
MODEL_NAME = "TinyLlama/TinyLlama-1.1B"
print(f"⏳ Chargement du modèle {MODEL_NAME}...")
try:
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    tokenizer.pad_token = tokenizer.eos_token
    print("✅ Tokenizer chargé.")
except Exception as e:
    print(f"❌ Erreur lors du chargement du tokenizer : {e}")
    exit(1)

# Configurer LoRA pour réduire la charge CPU
lora_config = LoraConfig(
    r=4,                  # Rang très petit pour le CPU
    lora_alpha=8,         # Facteur d'échelle
    target_modules=["q_proj", "v_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM",
)
print("✅ Configuration LoRA prête.")

# Charger le modèle en 8-bit (pour économiser de la RAM)
print("⏳ Chargement du modèle en 8-bit...")
try:
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        load_in_8bit=True,
        device_map="auto",
        torch_dtype=torch.float32,
    )
    print("✅ Modèle chargé en 8-bit.")
except Exception as e:
    print(f"❌ Erreur lors du chargement du modèle : {e}")
    print("🔄 Tentative avec un modèle plus petit (phi-2)...")
    MODEL_NAME = "microsoft/phi-2"
    try:
        model = AutoModelForCausalLM.from_pretrained(
            MODEL_NAME,
            device_map="auto",
            torch_dtype=torch.float32,
        )
        print(f"✅ Modèle {MODEL_NAME} chargé.")
    except Exception as e:
        print(f"❌ Échec du chargement du modèle de secours : {e}")
        exit(1)

# Appliquer LoRA
print("⏳ Application de LoRA...")
try:
    model = get_peft_model(model, lora_config)
    print("✅ LoRA appliqué.")
except Exception as e:
    print(f"❌ Erreur lors de l'application de LoRA : {e}")
    exit(1)

# Préparer le dataset
def tokenize_function(examples):
    prompts = [
        f"instruction: {instruction}\noutput: {code}"
        for instruction, code in zip(examples["instruction"], examples["code"])
    ]
    return tokenizer(
        prompts,
        padding="max_length",
        truncation=True,
        max_length=256,
    )

print("⏳ Tokenization du dataset...")
try:
    tokenized_dataset = dataset.map(tokenize_function, batched=True)
    print("✅ Dataset tokenisé.")
except Exception as e:
    print(f"❌ Erreur lors de la tokenization : {e}")
    exit(1)

# Configurer l'entraînement (CPU-friendly)
training_args = TrainingArguments(
    output_dir=OUTPUT_DIR,
    per_device_train_batch_size=1,
    gradient_accumulation_steps=4,
    learning_rate=2e-5,
    num_train_epochs=3,
    save_steps=100,
    logging_steps=10,
    save_total_limit=1,
    report_to="none",
    fp16=False,
    bf16=False,
    optim="adamw_torch",
)
print("✅ Configuration de l'entraînement prête.")

# Entraîner le modèle
print("⏳ Début de l'entraînement (3 époques)...")
try:
    from trl import SFTTrainer
    trainer = SFTTrainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_dataset,
        dataset_text_field="code",
        max_seq_length=256,
    )
    trainer.train()
    print("✅ Entraînement terminé !")
except ImportError:
    print("❌ La bibliothèque 'trl' n'est pas installée. Installation en cours...")
    import subprocess
    subprocess.run(["pip", "install", "trl"], check=True)
    from trl import SFTTrainer
    trainer = SFTTrainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_dataset,
        dataset_text_field="code",
        max_seq_length=256,
    )
    trainer.train()
    print("✅ Entraînement terminé !")
except Exception as e:
    print(f"❌ Erreur lors de l'entraînement : {e}")
    exit(1)

# Sauvegarder le modèle
print("⏳ Sauvegarde du modèle...")
try:
    model.save_pretrained(OUTPUT_DIR)
    tokenizer.save_pretrained(OUTPUT_DIR)
    print(f"✅ Modèle sauvegardé dans {OUTPUT_DIR}")
except Exception as e:
    print(f"❌ Erreur lors de la sauvegarde : {e}")
    exit(1)
