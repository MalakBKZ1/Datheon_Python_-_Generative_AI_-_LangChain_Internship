import shutil
import time
from pathlib import Path

from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from config import API_KEY, CHROMA_DIR, DOCS_DIR, EMBEDDING_MODEL


def load_documents():
    docs = []
    for f in sorted(Path(DOCS_DIR).iterdir()):
        if f.suffix.lower() == ".pdf":
            docs += PyPDFLoader(str(f)).load()          # 1 Document par page
        elif f.suffix.lower() in (".txt", ".md"):
            docs += TextLoader(str(f), encoding="utf-8").load()
    return docs


def main():
    docs = load_documents()
    if not docs:
        print("Aucun document trouvé dans documents/")
        return
    print(f"{len(docs)} pages/documents chargés.")

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    chunks = splitter.split_documents(docs)              # garde source et page en métadonnées
    print(f"{len(chunks)} morceaux créés.")

    if Path(CHROMA_DIR).exists():
        shutil.rmtree(CHROMA_DIR)                        # évite les doublons

    embeddings = GoogleGenerativeAIEmbeddings(model=EMBEDDING_MODEL, google_api_key=API_KEY)
    db = Chroma(
        collection_name="docs",
        embedding_function=embeddings,
        persist_directory=CHROMA_DIR,
    )

    batch_size = 50                                      # petits lots pour respecter le quota gratuit
    for i in range(0, len(chunks), batch_size):
        db.add_documents(chunks[i:i + batch_size])
        print(f"  {min(i + batch_size, len(chunks))}/{len(chunks)} indexés")
        time.sleep(2)

    print("Indexation terminée.")


if __name__ == "__main__":
    main()