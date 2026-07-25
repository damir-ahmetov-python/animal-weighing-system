import logging
import secrets

from app.db.crud import get_by_email, get_by_login, create_user

from fastapi import Depends, APIRouter, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from app.schemas import UserCreate, UserResponse, Token
from app.db.session import get_db
from app.core.security import create_access_token, decode_token, hash_password, verify_password
from app.db.crud import get_by_id, get_by_activation_token
from app.models import User

from app.core.config import settings
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/login')

def register(session: Session, login: str, email: str, password: str) -> UserResponse:
    """"Создаёт пользователя в неактивном состоянии, ждущего активации по email"""

    if get_by_email(email=email, session=session):
        raise HTTPException(status_code=409, detail='Email already exist')

    if get_by_login(session=session, login=login):
        raise HTTPException(status_code=409, detail='Login already exists')

    hashed_password = hash_password(password=password)

    activation_token = secrets.token_urlsafe(32)

    try:
        user = create_user(
            login=login,
            email=email,
            hashed_password=hashed_password.decode(),
            activation_token=activation_token,
            session=session
        )

        logger.info(f"User registered: {email} (login={login})")

        activation_link = f"/auth/activate/{activation_token}"
        logger.info(f"Activation link for {email}: {activation_link}")

        return user
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=409, detail='Login or email already exists')



def authenticate(session: Session, login: str, password: str) -> UserResponse:
    """
    Проверяет данные пользователя и возвращает его.

    Args:
        password: Пароль в открытом виде для проверки.

    Returns:
        Объект User, если учетные данные верны.

    Raises:
        HTTPException 400: Если пользователь не найден, не активирован или пароль неверный.
    """

    user = get_by_login(session=session, login=login)

    if not user:
        logger.warning(f"Failed login attempt: unknown login={login}")
        raise HTTPException(status_code=400, detail='User not found')

    if not user.is_active:
        logger.warning(f"Failed login attempt: user {login} is not active")
        raise HTTPException(status_code=400, detail='User is not active')

    if verify_password(password, user.hashed_password):
        return user
    else:
        logger.warning(f"Failed login attempt: incorrect password for {login}")
        raise HTTPException(status_code=400, detail='Incorrect password')


@router.post("/register", response_model=UserResponse)
def register_endpoints(user_data: UserCreate, session: Session = Depends(get_db)):
    user = register(
        login=user_data.login,
        email=user_data.email,
        password=user_data.password,
        session=session
    )

    return user

@router.post('/login', response_model=Token)
def login(session: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate(
        session=session,
        login=form_data.username,
        password=form_data.password
    )

    access_token = create_access_token({'sub': str(user.id)})

    return {'access_token': access_token, 'token_type': 'bearer'}

def activate(session: Session, token: str) -> UserResponse:
    user = get_by_activation_token(session=session, token=token)

    if not user:
        logger.warning(f"Activation failed: invalid token {token}")
        raise HTTPException(status_code=400, detail='Invalid activation token')

    if user.is_active:
        logger.warning(f"Activation failed: user {user.email} already activated")
        raise HTTPException(status_code=400, detail='User already activated')

    user.is_active = True
    user.activation_token = None

    session.commit()
    session.refresh(user)

    logger.info(f"User activated: {user.email}")

    return user


@router.get('/activate/{token}', response_model=UserResponse)
def activate_endpoint(token: str, session: Session = Depends(get_db)):
    return activate(session=session, token=token)


