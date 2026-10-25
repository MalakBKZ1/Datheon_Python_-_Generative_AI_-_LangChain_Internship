# Tâche 2 : assistant de questions-réponses avec RAG

Assistant qui répond à des questions uniquement à partir de documents PDF,
avec citation des pages sources.

## Pipeline
PDF → chargement (PyPDFLoader) → découpage récursif (chunk 1000, overlap 150)
→ embeddings Gemini → base vectorielle ChromaDB → recherche des 4 morceaux
les plus proches → prompt contraint → Gemini → réponse + sources

## Structure
```
task2-rag/
├── documents/    PDF (non versionnés)
├── config.py     paramètres (modèles, dossiers)
├── ingest.py     indexation
└── ask.py        questions-réponses
```

## Installation et utilisation
```bash
pip install -r requirements.txt
# placer un PDF dans task2-rag/documents/
cd task2-rag
python ingest.py
python ask.py
```
Document de démonstration : Lewis et al., « Retrieval-Augmented Generation for
Knowledge-Intensive NLP Tasks » (https://arxiv.org/abs/2005.11401).

## Exemples
| Question | Réponse (résumé) | Sources |
|---|---|---|
| ... | ... | ... |

Question hors sujet : « Je ne trouve pas la réponse dans les documents fournis. »

## Choix techniques
- LangChain : loaders, splitter, embeddings, vector store.
- Récupération et génération écrites explicitement plutôt qu'avec `RetrievalQA`,
  déplacé dans l'ancien paquet `langchain-classic` : code plus lisible et stable.
- `temperature=0` et consigne stricte pour limiter les réponses inventées.
- Réessais avec délai et modèle de secours (erreurs 503 et 429).

## Limites
- PDF scannés non gérés (pas d'OCR) ; pas de mémoire de conversation.
- Qualité dépendante de `chunk_size` et de `k`.