import ast
import math
import operator
from pathlib import Path

from google.genai import types

FILES_DIR = Path("files").resolve()
FILES_DIR.mkdir(exist_ok=True)


# ---------- Outil 1 : recherche web ----------
def web_search(query: str) -> str:
    try:
        from ddgs import DDGS
        results = DDGS().text(query, max_results=5)
    except Exception as e:
        return f"Erreur de recherche web : {e}"
    if not results:
        return "Aucun résultat."
    return "\n\n".join(f"{r['title']}\n{r['body']}\n{r['href']}" for r in results)


# ---------- Outil 2 : calculatrice sécurisée ----------
OPS = {
    ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
    ast.Div: operator.truediv, ast.Pow: operator.pow, ast.Mod: operator.mod,
    ast.FloorDiv: operator.floordiv, ast.USub: operator.neg, ast.UAdd: operator.pos,
}
FUNCS = {"sqrt": math.sqrt, "log": math.log, "abs": abs, "round": round}


def _eval(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in OPS:
        return OPS[type(node.op)](_eval(node.left), _eval(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in OPS:
        return OPS[type(node.op)](_eval(node.operand))
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in FUNCS:
        return FUNCS[node.func.id](*[_eval(a) for a in node.args])
    raise ValueError("expression non autorisée")


def calculator(expression: str) -> str:
    try:
        return str(_eval(ast.parse(expression, mode="eval").body))
    except Exception as e:
        return f"Erreur de calcul : {e}"


# ---------- Outil 3 : lecteur de fichiers locaux ----------
def read_file(filename: str) -> str:
    path = (FILES_DIR / filename).resolve()
    if FILES_DIR not in path.parents:          # empêche l'accès hors du dossier files/
        return "Accès refusé : seuls les fichiers du dossier files/ sont lisibles."
    if not path.exists():
        dispo = ", ".join(p.name for p in FILES_DIR.iterdir()) or "aucun"
        return f"Fichier introuvable : {filename}. Fichiers disponibles : {dispo}"
    try:
        if path.suffix.lower() == ".pdf":
            from pypdf import PdfReader
            text = "\n".join(p.extract_text() or "" for p in PdfReader(str(path)).pages)
        else:
            text = path.read_text(encoding="utf-8")
    except Exception as e:
        return f"Erreur de lecture : {e}"
    return text[:4000]


# ---------- Description des outils pour Gemini ----------
def _decl(name, description, param, param_desc):
    return types.FunctionDeclaration(
        name=name,
        description=description,
        parameters={
            "type": "OBJECT",
            "properties": {param: {"type": "STRING", "description": param_desc}},
            "required": [param],
        },
    )


TOOLS = types.Tool(function_declarations=[
    _decl("web_search",
          "Recherche sur le web pour obtenir des informations récentes ou factuelles.",
          "query", "Les mots-clés de la recherche."),
    _decl("calculator",
          "Calcule une expression mathématique (+ - * / ** %, sqrt, log, abs, round).",
          "expression", "L'expression à calculer, par exemple '12*85 + 5*420'."),
    _decl("read_file",
          "Lit un fichier local (txt, csv, md, pdf) du dossier files/.",
          "filename", "Le nom du fichier, par exemple 'ventes.csv'."),
])

FUNCTIONS = {"web_search": web_search, "calculator": calculator, "read_file": read_file}