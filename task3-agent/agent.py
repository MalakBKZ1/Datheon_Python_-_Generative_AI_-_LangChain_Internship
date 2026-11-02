import os
import time
from datetime import date

from dotenv import load_dotenv
from google import genai
from google.genai import errors, types

from tools import FUNCTIONS, TOOLS

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

MODELS = ["gemini-3.8-flash", "gemini-3.5-flash"]  # principal, puis secours
MAX_STEPS = 6                                       # évite les boucles infinies

SYSTEM = f"""Tu es un agent de recherche autonome. Date du jour : {date.today().isoformat()}.
Outils : web_search (infos récentes), calculator (tout calcul), read_file (fichiers du dossier files/).
Règles :
- Avant chaque appel d'outil, écris une phrase courte qui commence par "Pensée :" et explique pourquoi.
- N'invente jamais un chiffre : utilise calculator pour calculer et web_search pour l'actualité.
- Pour une question composée, enchaîne plusieurs outils.
- N'ajoute jamais d'unité ou de devise qui n'apparaît pas dans les données.
- Réponds en français et cite les URL des sources web utilisées."""

CONFIG = types.GenerateContentConfig(
    system_instruction=SYSTEM,
    tools=[TOOLS],
    automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),  # on gère la boucle
    temperature=0,
)


def call_gemini(contents, retries: int = 3):
    for model in MODELS:
        for attempt in range(retries):
            try:
                return client.models.generate_content(model=model, contents=contents, config=CONFIG)
            except (errors.ServerError, errors.ClientError) as e:
                if e.code not in (503, 429):
                    raise
                wait = 2 ** attempt * 5
                print(f"  {model} : erreur {e.code}, nouvel essai dans {wait} s...")
                time.sleep(wait)
    raise RuntimeError("Tous les modèles sont indisponibles.")


def run_agent(question: str):
    contents = [types.Content(role="user", parts=[types.Part(text=question)])]

    for step in range(1, MAX_STEPS + 1):
        print(f"\n--- Étape {step} ---")
        response = call_gemini(contents)
        content = response.candidates[0].content
        contents.append(content)                         # on garde la réponse du modèle dans l'historique
        calls = response.function_calls or []

        for part in content.parts or []:
            if part.text:
                text = part.text.strip()
                if calls:
                    text = text.removeprefix("Pensée :").strip()
                    print(f"Pensée : {text}")
                else:
                    print(f"Réponse finale : {text}")
        if not calls:                                    # plus d'outil demandé : c'est fini
            return

        result_parts = []
        for call in calls:
            args = dict(call.args or {})
            print(f"Action : {call.name}({args})")
            fn = FUNCTIONS.get(call.name)
            try:
                result = fn(**args) if fn else f"Outil inconnu : {call.name}"
            except Exception as e:
                result = f"Erreur d'exécution : {e}"
            print(f"Observation : {str(result)[:300]}")
            result_parts.append(
                types.Part.from_function_response(name=call.name, response={"result": result})
            )
        contents.append(types.Content(role="user", parts=result_parts))

    print("\nLimite d'étapes atteinte sans réponse finale.")


def main():
    print("Agent prêt. Tape 'q' pour quitter.")
    while True:
        question = input("\nQuestion : ").strip()
        if question.lower() in ("q", "quit", "exit"):
            break
        if question:
            run_agent(question)


if __name__ == "__main__":
    main()