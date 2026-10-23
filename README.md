# Tâche 1 : Pipeline de prompts LLM structurés et extracteur JSON

Extraction de données structurées (factures) à partir de texte non structuré,
avec l'API Gemini et une validation stricte par Pydantic.

## Fonctionnalités
- Template de prompt paramétré (`build_prompt`) avec exemple few-shot
- Sortie JSON contrainte par un schéma Pydantic (`response_schema`)
- Validation métier : quantité > 0, prix >= 0, vérification du total (TVA et remise incluses)
- Gestion des erreurs : réessais avec délai croissant (503 et 429) et modèle de secours
- Traitement par lot des fichiers de `samples/`, résultats dans `outputs/`

## Structure du projet
```
├── samples/        factures de test (.txt)
├── outputs/        résultats JSON validés
├── schemas.py      modèles Pydantic (Item, Invoice)
├── prompts.py      template de prompt et exemples few-shot
├── extractor.py    appel à Gemini, validation, traitement par lot
├── requirements.txt
└── .env.example
```

## Installation
```bash
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
```
Crée un fichier `.env` (non versionné) contenant :
```
GEMINI_API_KEY=ta_cle
```
La clé se crée gratuitement dans Google AI Studio.

## Utilisation
```bash
python extractor.py
```
Chaque fichier `samples/factureX.txt` produit un `outputs/factureX.json`.
Les fichiers déjà traités sont ignorés : vide `outputs/` pour tout régénérer.

## Exemple
Entrée :
```
Facture n° F-2026-014 du 15/10/2026
Client : Société Delta
2 x Clavier mécanique à 85 TND
1 x Écran 24 pouces à 420 TND
Total : 590 TND
```
Sortie :
```json
{
  "invoice_number": "F-2026-014",
  "date": "15/10/2026",
  "client_name": "Société Delta",
  "items": [
    {"description": "Clavier mécanique", "quantity": 2, "unit_price": 85.0},
    {"description": "Écran 24 pouces", "quantity": 1, "unit_price": 420.0}
  ],
  "total": 590.0,
  "currency": "TND"
}
```

## Cas de test
| Fichier | Cas testé |
|---|---|
| facture1 | facture simple |
| facture2 | TVA |
| facture3 | remise, virgules décimales |
| facture4 | devise absente, date écrite en lettres |
| facture5 | format désordonné, anglais, séparateur de milliers |

## Gestion des erreurs
- 503 (serveur surchargé) et 429 (quota) : réessais à 5, 10 puis 20 s,
  puis bascule sur un modèle de secours.
- Réponse invalide : `ValidationError` attrapée, le fichier est signalé
  et le traitement continue.
- Incohérence de total : avertissement affiché par `check_total`.

## Limites connues
- Les contraintes `Field(gt=0)` sont refusées par `response_schema` de Gemini
  (mot-clé `exclusiveMinimum`) : la validation métier est faite par des
  `field_validator` Pydantic après réception.
- Les noms de modèles Gemini évoluent : adapter la liste `MODELS` dans `extractor.py`.
- Les dates sont conservées telles qu'écrites dans le document.

## Pistes d'amélioration
- Extraction depuis des PDF ou images (OCR)
- Schéma `Resume` pour l'analyse de CV
- Tests unitaires sur les validateurs