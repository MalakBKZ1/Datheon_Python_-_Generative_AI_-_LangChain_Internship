import time

from google import genai
from google.genai import errors, types
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings

from config import API_KEY, CHAT_MODELS, CHROMA_DIR, EMBEDDING_MODEL

client = genai.Client(api_key=API_KEY)

PROMPT = """Tu es un assistant qui répond UNIQUEMENT à partir du contexte fourni.
Si la réponse n'est pas dans le contexte, réponds exactement :
"Je ne trouve pas la réponse dans les documents fournis."
N'utilise aucune connaissance extérieure. Réponds en français, de façon concise.

Contexte :
{context}

Question : {question}
"""


def load_db():
    embeddings = GoogleGenerativeAIEmbeddings(model=EMBEDDING_MODEL, google_api_key=API_KEY)
    return Chroma(collection_name="docs", embedding_function=embeddings, persist_directory=CHROMA_DIR)


def call_gemini(prompt: str, retries: int = 3):
    for model in CHAT_MODELS:
        for attempt in range(retries):
            try:
                return client.models.generate_content(
                    model=model,
                    contents=prompt,
                    config=types.GenerateContentConfig(temperature=0),
                )
            except (errors.ServerError, errors.ClientError) as e:
                if e.code not in (503, 429):
                    raise
                wait = 2 ** attempt * 5
                print(f"  {model} : erreur {e.code}, nouvel essai dans {wait} s...")
                time.sleep(wait)
    raise RuntimeError("Tous les modèles sont indisponibles.")


def answer(db, question: str, k: int = 4):
    results = db.similarity_search(question, k=k)        # k morceaux les plus proches

    context_parts, sources = [], []
    for doc in results:
        name = doc.metadata.get("source", "?").replace("\\", "/").split("/")[-1]
        page = doc.metadata.get("page")
        label = f"{name}, p. {page + 1}" if page is not None else name   # page est comptée depuis 0
        context_parts.append(f"[{label}]\n{doc.page_content}")
        if label not in sources:
            sources.append(label)

    prompt = PROMPT.format(context="\n\n".join(context_parts), question=question)
    response = call_gemini(prompt)
    return response.text, sources


def main():
    db = load_db()
    print("Assistant prêt. Tape 'q' pour quitter.")
    while True:
        question = input("\nQuestion : ").strip()
        if question.lower() in ("q", "quit", "exit"):
            break
        if not question:
            continue
        text, sources = answer(db, question)
        print("\nRéponse :", text)
        print("Sources :", " | ".join(sources))


if __name__ == "__main__":
    main()