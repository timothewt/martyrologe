import os
import json
import re
import time
from tqdm import tqdm
from glob import glob
from google import genai
from dotenv import load_dotenv

load_dotenv()
GEMINI_CLIENT = genai.Client()


def clean_json_string(raw: str) -> str:
    cleaned = re.sub(r"```(?:json)?", "", raw, flags=re.IGNORECASE)
    cleaned = cleaned.strip()
    return cleaned


def make_prompt(text: str) -> str:
    return f"""
Tu es un système d’extraction d’informations. 
Ta tâche : EXTRAIRE UNIQUEMENT ce qui est explicitement écrit dans le texte. 
Règles :
- Une seule entrée JSON par saint/martyr.
- Chaque entrée doit contenir exactement un "lieu", une "epoque", un "nom" et un "titre" (ex: évêque, abbé).
- Si le lieu ou l'époque n'est pas mentionné, mets "".
- Si aucun titre n'est mentionné, mets "aucun".
- **IMPORTANT : ne renvoie que le titre principal, concis** (ex : "évêque" au lieu de "évêque de cette ville").
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
    "titre": ""
  }}
]
"""


def ask_gemini(prompt: str) -> str:
    """Envoie la requête à l'API Gemini et retourne la réponse complète."""
    response = GEMINI_CLIENT.models.generate_content(
        model="gemini-2.5-flash-lite", contents=prompt
    )
    return response.text


def extract_martyrs_data(text: str) -> list[dict]:
    raw = ask_gemini(make_prompt(text))
    raw = clean_json_string(raw)

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        print("Erreur JSON pour le texte complet. Sauvegarde du texte pour debug.")
        with open("debug_failed.json", "w", encoding="utf-8") as f:
            f.write(raw)
        return []

    cleaned = []
    for entry in data:
        lieu = entry.get("lieu", "")
        epoque = entry.get("epoque", "")
        nom = entry.get("nom", "")
        titre = entry.get("titre", "aucun") or "aucun"

        cleaned.append({"lieu": lieu, "epoque": epoque, "nom": nom, "titre": titre})
    return cleaned


def main():
    files = sorted(glob("./data/raw/*.txt"))
    os.makedirs("./data/json", exist_ok=True)

    for filename in (t := tqdm(files)):
        t.set_postfix_str(filename)
        with open(filename, "r", encoding="utf-8") as f:
            text = f.read()

        martyrs_data = extract_martyrs_data(text)
        day = os.path.basename(filename)[:-4]

        with open(f"./data/json/{day}.json", "w", encoding="utf-8") as f:
            json.dump(martyrs_data, f, ensure_ascii=False, indent=2)

        time.sleep(6)

    print("Extraction terminée pour tous les fichiers.")


if __name__ == "__main__":
    main()
