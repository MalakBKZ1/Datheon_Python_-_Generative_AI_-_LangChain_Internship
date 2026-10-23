import time
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types, errors
from pydantic import ValidationError

from prompts import build_prompt
from schemas import Invoice

load_dotenv()
client = genai.Client()

MODELS = ["gemini-3.8-flash", "gemini-3.5-flash"]  # modèle principal, puis secours


# ---------- Appel à Gemini avec réessais et modèle de secours ----------
def call_gemini(prompt: str, schema, retries: int = 3):
    for model in MODELS:
        for attempt in range(retries):
            try:
                return client.models.generate_content(
                    model=model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=schema,
                        temperature=0,
                    ),
                )
            except (errors.ServerError, errors.ClientError) as e:
                if e.code not in (503, 429):
                    raise
                wait = 2 ** attempt * 5
                print(f"  {model} : erreur {e.code}, nouvel essai dans {wait} s...")
                time.sleep(wait)
        print(f"  {model} indisponible, passage au modèle suivant...")
    raise RuntimeError("Tous les modèles sont indisponibles.")


# ---------- Extraction + validation ----------
def extract_invoice(text: str) -> Invoice:
    response = call_gemini(build_prompt(text), Invoice)
    return Invoice.model_validate_json(response.text)  # lève ValidationError si invalide


def check_total(invoice: Invoice) -> None:
    calculated = sum(i.quantity * i.unit_price for i in invoice.items)
    calculated -= abs(invoice.discount_amount or 0)
    calculated += invoice.tax_amount or 0
    if abs(calculated - invoice.total) > 0.01:
        print(f"  Attention : total calculé {calculated} différent du total extrait {invoice.total}")


# ---------- Traitement de plusieurs documents ----------
def main():
    samples_dir = Path("samples")
    outputs_dir = Path("outputs")
    outputs_dir.mkdir(exist_ok=True)

    files = sorted(samples_dir.glob("*.txt"))
    if not files:
        print("Aucun fichier .txt trouvé dans le dossier samples/")
        return

    for file in files:
        out_file = outputs_dir / f"{file.stem}.json"
        if out_file.exists():
            print(f"{file.name} déjà traité, ignoré.")
            continue

        print(f"Traitement de {file.name}...")
        text = file.read_text(encoding="utf-8")
        try:
            invoice = extract_invoice(text)
            check_total(invoice)
            out_file.write_text(invoice.model_dump_json(indent=2), encoding="utf-8")
            print(f"  OK -> {out_file}")
        except ValidationError as e:
            print(f"  JSON invalide pour {file.name} : {e}")
        except Exception as e:
            print(f"  Échec pour {file.name} : {e}")
        time.sleep(2)  # évite de dépasser le quota gratuit


if __name__ == "__main__":
    main()