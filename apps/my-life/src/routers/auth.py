from fastapi import APIRouter, Response, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from ..auth import login, logout, verify_session

router = APIRouter(prefix="/api/auth", tags=["auth"])


class LoginBody(BaseModel):
    password: str


@router.post("/login")
def do_login(body: LoginBody, response: Response):
    ok = login(body.password, response)
    if not ok:
        return JSONResponse({"ok": False, "error": "wrong password"}, status_code=401)
    return {"ok": True}


@router.post("/logout")
def do_logout(request: Request, response: Response):
    logout(request, response)
    return {"ok": True}


@router.get("/status")
def status(request: Request):
    return {"authenticated": verify_session(request)}
