import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
EMBEDDING_MODEL = "models/gemini-embedding-001"
CHAT_MODELS = ["gemini-3.8-flash", "gemini-3.5-flash"]  # principal, puis secours
DOCS_DIR = "documents"
CHROMA_DIR = "chroma_db"
