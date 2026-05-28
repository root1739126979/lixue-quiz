from datetime import datetime, timedelta, timezone
import base64
import hashlib
import hmac
import json
import os
from typing import Any

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import User


security_scheme = HTTPBearer(auto_error=False)


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _b64url_decode(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 200_000)
    return f"pbkdf2_sha256${_b64url_encode(salt)}${_b64url_encode(digest)}"


def verify_password(password: str, password_hash: str) -> bool:
    try:
        algorithm, salt_text, digest_text = password_hash.split("$", 2)
    except ValueError:
        return False
    if algorithm != "pbkdf2_sha256":
        return False
    salt = _b64url_decode(salt_text)
    expected = _b64url_decode(digest_text)
    actual = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 200_000)
    return hmac.compare_digest(actual, expected)


def create_access_token(subject: str, role: str) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expire_minutes)
    payload = {"sub": subject, "role": role, "exp": int(expires_at.timestamp())}
    signing_input = ".".join(
        [
            _b64url_encode(json.dumps(header, separators=(",", ":")).encode("utf-8")),
            _b64url_encode(json.dumps(payload, separators=(",", ":")).encode("utf-8")),
        ]
    )
    signature = hmac.new(
        settings.jwt_secret.encode("utf-8"),
        signing_input.encode("ascii"),
        hashlib.sha256,
    ).digest()
    return f"{signing_input}.{_b64url_encode(signature)}"


def decode_access_token(token: str) -> dict[str, Any]:
    try:
        header_text, payload_text, signature_text = token.split(".", 2)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="无效 token") from exc

    signing_input = f"{header_text}.{payload_text}"
    expected_signature = hmac.new(
        settings.jwt_secret.encode("utf-8"),
        signing_input.encode("ascii"),
        hashlib.sha256,
    ).digest()
    if not hmac.compare_digest(_b64url_decode(signature_text), expected_signature):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="无效 token")

    payload = json.loads(_b64url_decode(payload_text))
    if int(payload.get("exp", 0)) < int(datetime.now(timezone.utc).timestamp()):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="token 已过期")
    return payload


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security_scheme),
    db: Session = Depends(get_db),
) -> User:
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="未登录")
    payload = decode_access_token(credentials.credentials)
    if payload.get("role") != "employee":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="权限不足")
    user = db.get(User, int(payload["sub"]))
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="账号不可用")
    return user


def get_current_admin(
    credentials: HTTPAuthorizationCredentials | None = Depends(security_scheme),
) -> dict[str, str]:
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="未登录")
    payload = decode_access_token(credentials.credentials)
    if payload.get("role") != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="权限不足")
    return {"username": str(payload.get("sub", ""))}
