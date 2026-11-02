# Tâche 3 : agent autonome multi-outils

Agent console qui choisit et enchaîne seul des outils pour résoudre des
questions composées. Il affiche son raisonnement : pensée → action →
observation → réponse finale.

## Outils
| Outil | Rôle |
|---|---|
| web_search | recherche web (DuckDuckGo via `ddgs`) |
| calculator | calculs sécurisés (module `ast`, pas de `eval`) |
| read_file | lecture de fichiers txt, csv, md, pdf du dossier `files/` |

## Fonctionnement
Boucle explicite avec le function calling de Gemini : le modèle demande un
outil, le code l'exécute, le résultat revient au modèle, jusqu'à la réponse
finale (6 étapes maximum).

## Installation et utilisation
    pip install -r requirements.txt
    cd task3-agent
    python agent.py

## Exemple de trace
(colle ici ta capture ou la trace de la question à trois outils)

## Choix techniques et sécurité
- Boucle écrite à la main plutôt que les anciennes classes d'agents LangChain :
  plus lisible, plus stable, raisonnement entièrement visible.
- Lecteur de fichiers limité au dossier `files/`.
- Calculatrice limitée aux opérations arithmétiques autorisées.
- Réessais avec délai et modèle de secours (erreurs 503 et 429).
- Règles de prompt : ne pas inventer de chiffres, d'unités ni de devises.

## Limites
- `read_file` tronque à 4000 caractères (signalé à l'agent).
- La recherche DuckDuckGo peut être limitée en débit ; les résultats web
  doivent être vérifiés.
- Pas de mémoire entre deux questions.