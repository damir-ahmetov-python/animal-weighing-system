import bcrypt
from fastapi import HTTPException
from app.core.config import settings
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone

SECRET_KEY = settings.jwt.secret_key
ALGORITHM = settings.jwt.algorithm
TTL = settings.jwt.access_token_expire_minutes


def hash_password(password: str) -> bytes:
    """
    Хеширует пароль с использованием bcrypt.

    Args:
        password: Пароль в открытом виде.

    Returns:
        Хешированный пароль в виде байтовой строки.
    """

    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password=password.encode(), salt=salt)

    return hashed_password


def verify_password(plain: str, hashed: str) -> bool:
    """
    Проверяет, соответствует ли открытый пароль сохранённому хешу.

    Args:
        plain: Пароль в открытом виде.
    """
    return bcrypt.checkpw(plain.encode(), hashed.encode())


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=TTL)
    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


def decode_token(token: str) -> dict:
    """
    Декодирует JWT-токен и возвращает его содержимое.

    Args:
        token: JWT-токен в виде строки.

    Returns:
        Словарь с данными из токена (payload).

    Raises:
        Ошибка валидации, если токен недействителен или подпись не совпадает.
    """

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=401,
            detail='Could not validate credentials'
        )