PROMPT_TEMPLATE = """Tu es un assistant d'extraction de données.
Extrais les informations du {doc_type} ci-dessous.
Réponds uniquement avec un JSON valide.
Si une information est absente, mets null. N'invente rien.

{examples}

Texte à analyser :
{text}
"""

INVOICE_EXAMPLES = """Exemple :
Texte :
Facture n° F-2025-001 du 03/02/2025
Client : Société Alpha
3 x Souris à 20 TND
Total : 60 TND

Résultat :
{"invoice_number": "F-2025-001", "date": "03/02/2025", "client_name": "Société Alpha",
 "items": [{"description": "Souris", "quantity": 3, "unit_price": 20.0}],
 "total": 60.0, "currency": "TND", "tax_amount": null, "discount_amount": null}
"""


def build_prompt(text: str, doc_type: str = "facture", examples: str = INVOICE_EXAMPLES) -> str:
    return PROMPT_TEMPLATE.format(doc_type=doc_type, examples=examples, text=text)