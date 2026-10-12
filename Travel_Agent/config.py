import os
from pathlib import Path
from dotenv import load_dotenv

# Resolve workspace root reliably regardless of current working directory
WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
env_path = WORKSPACE_ROOT / ".env"
load_dotenv(dotenv_path=env_path)

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama3-8b-8192")
GROQ_BASE_URL = os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1")


def is_groq_configured() -> bool:
    """Returns True if a non-empty GROQ_API_KEY is detected."""
    return bool(GROQ_API_KEY and GROQ_API_KEY.strip())

