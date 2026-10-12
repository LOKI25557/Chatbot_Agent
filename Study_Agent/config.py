import os
from pathlib import Path
from typing import Tuple
from dotenv import load_dotenv

# Resolve paths
STUDY_AGENT_DIR = Path(__file__).resolve().parent
WORKSPACE_ROOT = STUDY_AGENT_DIR.parent

# Check for .env in local Study_Agent folder first, then parent workspace root
local_env = STUDY_AGENT_DIR / ".env"
root_env = WORKSPACE_ROOT / ".env"

if local_env.exists():
    load_dotenv(dotenv_path=local_env)
elif root_env.exists():
    load_dotenv(dotenv_path=root_env)
else:
    load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile").strip()
GROQ_BASE_URL = os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1").strip()


def is_groq_configured() -> bool:
    """Returns True if a non-empty GROQ_API_KEY is available."""
    return bool(GROQ_API_KEY)


def verify_groq_connection(timeout: float = 5.0) -> Tuple[bool, str]:
    """
    Safely tests Groq API connectivity without leaking secrets in logs or responses.
    Returns (True, 'Connected') on success, or (False, error_summary) on failure.
    """
    if not is_groq_configured():
        return False, "API key not configured (GROQ_API_KEY is missing)"

    try:
        from openai import OpenAI
        client = OpenAI(
            api_key=GROQ_API_KEY,
            base_url=GROQ_BASE_URL,
            timeout=timeout
        )
        # Minimal single-token connectivity test
        client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "user", "content": "ping"}],
            max_tokens=1,
            timeout=timeout
        )
        return True, "API Connected"
    except Exception as e:
        err_msg = str(e).lower()
        if "decommissioned" in err_msg:
            return False, f"Configured model '{GROQ_MODEL}' is decommissioned on Groq"
        if "authentication" in err_msg or "401" in err_msg or "invalid_api_key" in err_msg:
            return False, "Authentication failed (invalid API key)"
        if "rate_limit" in err_msg or "429" in err_msg:
            return False, "Rate limit exceeded (429)"
        if "model_not_found" in err_msg or "404" in err_msg:
            return False, f"Model '{GROQ_MODEL}' not found"
        if "timeout" in err_msg or "connection" in err_msg:
            return False, "Network connection timed out"
        return False, f"API test failed ({type(e).__name__})"
