from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from mysite.config import settings
from mysite.database.db import get_db
from mysite.database.model import User,Role
from ..database.schema import (
    AccessResponseSchema,
    TokenResponseSchema,
    UserCreate,
    UserLoginSchema,
)

auth_router = APIRouter(prefix="/auth", tags=["Authorization"])
bearer = HTTPBearer(auto_error=False)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_token(subject: str, token_type: str, expires_delta: timedelta) -> str:
    payload = {
        "sub": subject,
        "type": token_type,
        "exp": datetime.now(timezone.utc) + expires_delta,
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_access_token(user_id: int) -> str:
    return create_token(
        str(user_id), "access", timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )


def create_refresh_token(user_id: int) -> str:
    return create_token(
        str(user_id), "refresh", timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    )

async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
    db: AsyncSession = Depends(get_db),
) -> User:
    # Без токена нельзя определить пользователя.
    if credentials is None:
        raise HTTPException(
            status_code=401,
            detail="Нужно войти в аккаунт",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Твоя функция проверяет подпись, срок и тип токена.
    user_id = decode_token(
        credentials.credentials,
        expected_type="access",
    )

    # Получаем пользователя по id из токена.
    user = await db.get(User, user_id)

    if user is None or not user.is_active:
        raise HTTPException(
            status_code=401,
            detail="Пользователь отсутствует или отключён",
        )

    return user


def decode_token(token: str, expected_type: str) -> int:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        if payload.get("type") != expected_type:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
            )
        return int(payload["sub"])
    except (JWTError, KeyError, TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )


@auth_router.post("/register/", status_code=201)
async def register(
    data: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    email = str(data.email)

    query = select(User).where(User.email == email)
    existing = (await db.execute(query)).scalars().first()

    if existing is not None:
        raise HTTPException(
            status_code=409,
            detail="Этот email уже зарегистрирован",
        )

    user = User(
        full_name=data.full_name,
        email=str(data.email),
        password=hash_password(data.password),
        role=data.role,
        updated_at=datetime.now(timezone.utc),
    )

    db.add(user)
    await db.commit()
    return {"message": "Регистрация успешна"}


@auth_router.post("/login/", response_model=TokenResponseSchema)
async def login(data: UserLoginSchema, db: AsyncSession = Depends(get_db)):
    query = select(User).where(User.email == str(data.email))
    user = (await db.execute(query)).scalars().first()
    if user is None or not verify_password(data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )
    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)
    user.refresh_token = refresh_token
    await db.commit()
    return TokenResponseSchema(access_token=access_token, refresh_token=refresh_token)


@auth_router.post("/refresh/", response_model=AccessResponseSchema)
async def refresh(
    refresh_token: str = Query(...), db: AsyncSession = Depends(get_db)
):
    user_id = decode_token(refresh_token, expected_type="refresh")
    user = await db.get(User, user_id)
    if user is None or user.refresh_token != refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token is invalid or revoked",
        )
    return AccessResponseSchema(access_token=create_access_token(user.id))


@auth_router.post("/logout/")
async def logout(
    refresh_token: str = Query(...), db: AsyncSession = Depends(get_db)
):
    user_id = decode_token(refresh_token, expected_type="refresh")
    user = await db.get(User, user_id)
    if user is None or user.refresh_token != refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token is invalid or revoked",
        )
    user.refresh_token = None
    await db.commit()
    return {"message": "Ийгиликтуу чыгып кеттиниз"}
