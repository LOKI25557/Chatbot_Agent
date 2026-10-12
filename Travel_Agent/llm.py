import json
import re
from typing import Tuple
from openai import OpenAI
from config import GROQ_API_KEY, GROQ_BASE_URL, GROQ_MODEL, is_groq_configured

def get_client() -> OpenAI:
    """Initialize and return the OpenAI client configured for Groq with a sensible timeout."""
    return OpenAI(
        api_key=GROQ_API_KEY,
        base_url=GROQ_BASE_URL,
        timeout=15.0
    )


def verify_groq_connection(timeout: float = 5.0) -> Tuple[bool, str]:
    """
    Safely verify Groq API connectivity without exposing credentials.
    Returns (True, 'Connected') on success, or (False, error_category) on failure.
    """
    if not is_groq_configured():
        return False, "API key not configured (Demo Mode active)"

    try:
        client = get_client()
        # Perform a minimal 1-token test with configured model
        client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "user", "content": "ping"}],
            max_tokens=1,
            timeout=timeout
        )
        return True, "API Connected"
    except Exception as e:
        err_type = type(e).__name__
        err_msg = str(e)
        if "decommissioned" in err_msg.lower():
            return False, f"Model '{GROQ_MODEL}' is decommissioned on Groq"
        if "authentication" in err_msg.lower() or "401" in err_msg or "invalid_api_key" in err_msg:
            return False, "Authentication failed (invalid API key)"
        if "rate_limit" in err_msg.lower() or "429" in err_msg:
            return False, "Rate limit exceeded (429)"
        if "model_not_found" in err_msg.lower() or "404" in err_msg:
            return False, f"Model '{GROQ_MODEL}' not found on Groq"
        if "connection" in err_msg.lower() or "timeout" in err_msg.lower():
            return False, "Network connection timeout"
        return False, f"{err_type}: API request failed"

def parse_travel_request(user_request: str) -> dict:
    """Use the LLM to parse a natural language travel request into a structured JSON dict."""
    if not is_groq_configured():
        # DEMO MODE fallback parsing
        return _demo_parse_request(user_request)

    client = get_client()
    prompt = f"""
    Extract the travel details from the following request.
    Return ONLY a JSON object with these exact keys:
    - source (string)
    - destination (string)
    - duration_days (integer)
    - budget (float)
    - preferences (list of strings)
    
    Request: "{user_request}"
    """
    try:
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.0
        )
        content = response.choices[0].message.content
        if content:
            cleaned = content.strip()
            # Strip markdown code blocks if returned
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            elif cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            parsed = json.loads(cleaned.strip())
            return {
                "source": str(parsed.get("source", "City")),
                "destination": str(parsed.get("destination", "Destination")),
                "duration_days": int(parsed.get("duration_days", 3)),
                "budget": float(parsed.get("budget", 15000.0)),
                "preferences": list(parsed.get("preferences", []))
            }
        return _demo_parse_request(user_request)
    except Exception as e:
        # Gracefully fall back to deterministic demo parsing
        return _demo_parse_request(user_request)

def generate_reasoning(context: str, issue: str) -> str:
    """Use the LLM to explain reasoning when encountering an issue."""
    if not is_groq_configured():
        return f"Deterministic rule matched: {issue}. Attempting alternative."

    client = get_client()
    prompt = f"""
    You are a travel agent reasoning engine. 
    Context: {context}
    Issue encountered: {issue}
    Explain in one short sentence what you will do to resolve this issue and replan.
    """
    try:
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        content = response.choices[0].message.content
        return content.strip() if content else f"Will resolve {issue}."
    except Exception:
        return f"Deterministic alternative selected for: {issue}."

def _demo_parse_request(request: str) -> dict:
    """Deterministic extraction for demo requests without relying on external API."""
    req_lower = request.lower()
    
    # Source & destination extraction
    source = "Bengaluru"
    destination = "Goa"
    src_match = re.search(r"from\s+([A-Za-z]+)\s+to\s+([A-Za-z]+)", request, re.IGNORECASE)
    if src_match:
        source = src_match.group(1).capitalize()
        destination = src_match.group(2).capitalize()
    else:
        if "goa" in req_lower:
            destination = "Goa"
        if "bengaluru" in req_lower or "bangalore" in req_lower:
            source = "Bengaluru"

    # Duration extraction
    duration = 3
    dur_match = re.search(r"(\d+)\s*days?", req_lower)
    if dur_match:
        duration = max(1, int(dur_match.group(1)))

    # Budget extraction
    budget = 15000.0
    budget_clean = req_lower.replace(",", "")
    b_match = re.search(r"(?:under|budget|₹|rs\.?)\s*(\d+)", budget_clean)
    if b_match:
        budget = float(b_match.group(1))
    elif "15000" in budget_clean:
        budget = 15000.0

    # Preferences extraction
    prefs = []
    if "beach" in req_lower:
        prefs.append("beaches")
    if "sightseeing" in req_lower:
        prefs.append("sightseeing")
    if "vegetarian" in req_lower:
        prefs.append("vegetarian food")
    if not prefs:
        prefs = ["sightseeing"]

    return {
        "source": source,
        "destination": destination,
        "duration_days": duration,
        "budget": budget,
        "preferences": prefs
    }

