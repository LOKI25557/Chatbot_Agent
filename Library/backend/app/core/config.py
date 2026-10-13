import os
from pathlib import Path
from typing import List
from dotenv import load_dotenv

# Resolve directory paths
BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
LIBRARY_DIR = BACKEND_DIR.parent
WORKSPACE_ROOT = LIBRARY_DIR.parent

# Load .env: local backend first, then Library/, then workspace root
local_env = BACKEND_DIR / ".env"
library_env = LIBRARY_DIR / ".env"
root_env = WORKSPACE_ROOT / ".env"

if local_env.exists():
    load_dotenv(dotenv_path=local_env)
elif library_env.exists():
    load_dotenv(dotenv_path=library_env)
elif root_env.exists():
    load_dotenv(dotenv_path=root_env)
else:
    load_dotenv()


class Settings:
    PROJECT_NAME: str = "AI-Powered Library Agent"
    VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{BACKEND_DIR / 'library.db'}")

    # AI Configuration (reusing existing Groq configuration securely)
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "").strip()
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile").strip()
    GROQ_BASE_URL: str = os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1").strip()

    @property
    def clean_groq_base_url(self) -> str:
        raw = self.GROQ_BASE_URL.strip()
        if not raw:
            return "https://api.groq.com"
        return raw.replace("/openai/v1", "").rstrip("/")

    # Security
    ADMIN_SECRET_KEY: str = os.getenv("ADMIN_SECRET_KEY", "library-admin-secret-2026").strip()

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://localhost:8000",
        "http://127.0.0.1:8000"
    ]

    def is_groq_configured(self) -> bool:
        return bool(self.GROQ_API_KEY)


settings = Settings()
