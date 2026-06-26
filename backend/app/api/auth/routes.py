import uuid
from datetime import datetime, timedelta, timezone

import bcrypt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from pydantic import BaseModel

from app.config import settings
from app.db.database import get_connection
from app.models.schemas import LoginRequest, RegisterRequest, TokenResponse, UserOut

router = APIRouter()
security = HTTPBearer(auto_error=False)

ALGORITHM = "HS256"


class RefreshTokenBody(BaseModel):
    refresh_token: str


def _ensure_users_table() -> None:
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                hashed_password TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'engineer',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.commit()


def _seed_admin() -> None:
    with get_connection() as conn:
        existing = conn.execute(
            "SELECT id FROM users WHERE email = ?", ("admin@intelliplant.ai",)
        ).fetchone()
        if existing is None:
            hashed = bcrypt.hashpw(b"password123", bcrypt.gensalt()).decode("utf-8")
            uid = str(uuid.uuid4())
            conn.execute(
                "INSERT INTO users (id, email, name, hashed_password, role) VALUES (?, ?, ?, ?, ?)",
                (uid, "admin@intelliplant.ai", "Admin", hashed, "admin"),
            )
            conn.commit()


_ensure_users_table()
_seed_admin()


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    )
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, settings.secret_key, algorithm=ALGORITHM)


def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, settings.secret_key, algorithm=ALGORITHM)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))


def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> dict:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
        )
    try:
        payload = jwt.decode(
            credentials.credentials, settings.secret_key, algorithms=[ALGORITHM]
        )
        email: str | None = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )

    with get_connection() as conn:
        user = conn.execute(
            "SELECT id, email, name, role FROM users WHERE email = ?", (email,)
        ).fetchone()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
        )
    return dict(user)


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest) -> dict:
    with get_connection() as conn:
        user = conn.execute(
            "SELECT id, email, name, hashed_password, role FROM users WHERE email = ?",
            (payload.email,),
        ).fetchone()

    if user is None or not verify_password(payload.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )

    user_dict = dict(user)
    token_data = {"sub": user_dict["email"]}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {
            "id": user_dict["id"],
            "email": user_dict["email"],
            "name": user_dict["name"],
            "role": user_dict["role"],
        },
    }


@router.post("/register", response_model=UserOut)
def register(payload: RegisterRequest) -> dict:
    hashed = get_password_hash(payload.password)
    uid = str(uuid.uuid4())

    with get_connection() as conn:
        try:
            conn.execute(
                "INSERT INTO users (id, email, name, hashed_password, role) VALUES (?, ?, ?, ?, ?)",
                (uid, payload.email, payload.name, hashed, "engineer"),
            )
            conn.commit()
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
            )

    return {
        "id": uid,
        "email": payload.email,
        "name": payload.name,
        "role": "engineer",
    }


@router.get("/me")
def me(current_user: dict = Depends(get_current_user)) -> dict:
    return current_user


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(body: RefreshTokenBody) -> dict:
    try:
        payload = jwt.decode(
            body.refresh_token, settings.secret_key, algorithms=[ALGORITHM]
        )
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type"
            )
        email: str | None = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        )

    with get_connection() as conn:
        user = conn.execute(
            "SELECT id, email, name, role FROM users WHERE email = ?", (email,)
        ).fetchone()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
        )

    user_dict = dict(user)
    token_data = {"sub": user_dict["email"]}
    new_access_token = create_access_token(token_data)
    new_refresh_token = create_refresh_token(token_data)

    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
        "user": user_dict,
    }
