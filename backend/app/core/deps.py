from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.security import decode_token
from app.db.crud import get_by_id
from app.db.session import get_db
from app.models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/login')


def get_current_user(token: str = Depends(oauth2_scheme), session: Session = Depends(get_db)) -> User:
    """
    Возвращает текущего пользователя по JWT-токену из запроса.

    Args:
        token: JWT-токен, извлечённый из заголовка Authorization.
        session: сессия SQLAlchemy.

    Returns:
        Объект User, соответствующий токену.

    Raises:
        HTTPException 401: Если токен невалиден или пользователь не найден.
    """

    payload = decode_token(token=token)

    try:
        user_id = int(payload.get('sub'))
    except (TypeError, ValueError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate credentials')

    user = get_by_id(session=session, user_id=user_id)

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate credentials')

    return user


def require_admin(user: User = Depends(get_current_user)) -> User:
    """
    Проверяет, что текущий пользователь имеет роль admin.

    Args:
        user: Текущий пользователь (из get_current_user).

    Returns:
        Объект User, если у пользователя роль admin.

    Raises:
        HTTPException 403: Если у пользователя нет прав администратора.
    """

    if user.role != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Admin privileges required')

    return user