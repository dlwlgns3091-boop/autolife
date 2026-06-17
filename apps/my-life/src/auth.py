import os
import secrets
from fastapi import Request, Response, HTTPException

SESSION_COOKIE = "mylife_session"
_valid_tokens: set[str] = set()

APP_PASSWORD = os.environ.get("APP_PASSWORD", "")


def verify_session(request: Request) -> bool:
    token = request.cookies.get(SESSION_COOKIE)
    return token is not None and token in _valid_tokens


def require_auth(request: Request):
    if not verify_session(request):
        raise HTTPException(status_code=401, detail="Unauthorized")


def login(password: str, response: Response) -> bool:
    if not APP_PASSWORD:
        raise RuntimeError("APP_PASSWORD environment variable is not set")
    if password != APP_PASSWORD:
        return False
    token = secrets.token_hex(32)
    _valid_tokens.add(token)
    response.set_cookie(
        SESSION_COOKIE,
        token,
        httponly=True,
        samesite="lax",
        max_age=60 * 60 * 24 * 30,  # 30 days
    )
    return True


def logout(request: Request, response: Response):
    token = request.cookies.get(SESSION_COOKIE)
    if token:
        _valid_tokens.discard(token)
    response.delete_cookie(SESSION_COOKIE)
