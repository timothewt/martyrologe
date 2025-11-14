import os
import requests
import json
from glob import glob


# -------------------------------
# Prompt builder
# -------------------------------
def make_prompt(text: str) -> str:
    return f"""
Tu es un système d’extraction d’informations. 
Ta tâche : EXTRAIRE UNIQUEMENT ce qui est explicitement écrit dans le texte. 
Règles :
- Une seule entrée JSON par saint/martyr.
- Chaque entrée doit contenir exactement un "lieu", une "epoque", un "nom" et une liste de "titres".
- Si le lieu ou l'époque n'est pas mentionné, mets "".
- Si aucun titre n'est mentionné, mets ["aucun"].
- Ne rien inventer, ne rien inférer.
- Pas de texte hors du JSON.

Texte source :
{text}

Renvoie UNIQUEMENT un JSON sous forme de liste :
[
  {{
    "lieu": "",
    "epoque": "",
    "nom": "",
    "titres": []
  }}
]
"""


# -------------------------------
# Ollama API
# -------------------------------
def ask_ollama(prompt: str, model: str = "mistral:instruct") -> str:
    """Envoie la requête à Ollama et récupère la réponse complète."""
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={"model": model, "prompt": prompt, "num_predict": 500},
        stream=True,
    )

    full_output = ""
    for line in response.iter_lines():
        if not line:
            continue
        data = json.loads(line.decode("utf-8"))
        if "response" in data:
            full_output += data["response"]

    return full_output


# -------------------------------
# Extraction + nettoyage
# -------------------------------
def extract_martyrs_data(text: str) -> list[dict]:
    """Extrait chaque saint individuellement, avec une entrée par saint."""
    raw = ask_ollama(make_prompt(text))
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        print("Erreur JSON pour le texte complet")
        return []

    cleaned = []
    for entry in data:
        lieu = entry.get("lieu", "")
        epoque = entry.get("epoque", "")
        nom = entry.get("nom", "")
        titres = entry.get("titres", ["aucun"])

        if not titres:
            titres = ["aucun"]

        cleaned.append({"lieu": lieu, "epoque": epoque, "nom": nom, "titres": titres})
    return cleaned


# -------------------------------
# Script principal
# -------------------------------
def main():
    files = sorted(glob("./data/raw/*.txt"))
    os.makedirs("./data/clean", exist_ok=True)

    for filename in files:
        print(f"Traitement du fichier : {filename}")
        with open(filename, "r", encoding="utf-8") as f:
            text = f.read()

        martyrs_data = extract_martyrs_data(text)
        day = os.path.basename(filename)[:-4]

        with open(f"./data/clean/{day}.json", "w", encoding="utf-8") as f:
            json.dump(martyrs_data, f, ensure_ascii=False, indent=2)

    print("Extraction terminée pour tous les fichiers.")


if __name__ == "__main__":
    main()
