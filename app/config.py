import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "analytics.db"
LOG_PATH = BASE_DIR / "logs" / "audit.jsonl"
MODEL_NAME = os.getenv("OLLAMA_MODEL") or os.getenv("OPENAI_MODEL", "llama3.2")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
MAX_ROWS = 50
MAX_RETRIES = 2
