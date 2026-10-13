import hmac
from fastapi import Header, HTTPException, status
from app.core.config import settings


def verify_admin_access(x_admin_key: str = Header(None, alias="X-Admin-Key")) -> bool:
    """
    Validates administrative requests via secure timing-attack-safe comparison
    of the secret key provided in the X-Admin-Key header.
    """
    if not x_admin_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Admin authentication required. Missing 'X-Admin-Key' header."
        )

    # Constant-time comparison to prevent timing attacks
    if not hmac.compare_digest(x_admin_key.strip(), settings.ADMIN_SECRET_KEY):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid administrator key provided."
        )

    return True
