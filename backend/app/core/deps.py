from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.security import decode_token
from app.db.crud import get_by_id, get_weighting_by_id, get_animal_type_by_id, get_breed_by_id, get_animal_by_id
from app.db.session import get_db
from app.models import User, Weighting, AnimalType, Breed, Animal

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
        raise HTTPException(status_code=401, detail='Could not validate credentials')

    user = get_by_id(session=session, user_id=user_id)

    if not user:
        raise HTTPException(status_code=401, detail='Could not validate credentials')

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
        raise HTTPException(status_code=403, detail='Admin privileges required')

    return user

def get_weighting(
    weighting_id: int,
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Weighting:
    """Находит запись взвешивания по id и проверяет доступ: admin видит любую
    запись, обычный пользователь - только свою (иначе 404, не 403 - чтобы
    не палить сам факт существования чужой записи)."""
    weighting = get_weighting_by_id(session=session, weighting_id=weighting_id)

    if not weighting or (current_user.role != 'admin' and weighting.created_by_user_id != current_user.id):
        raise HTTPException(status_code=404, detail="Weighting not found")

    return weighting

def require_animal_type(type_id: int, session: Session = Depends(get_db)) -> AnimalType:
    """Находит тип животного по id либо кидает 404 - убирает дублирование
    этой проверки в get/update/delete эндпоинтах catalog.py."""
    animal_type = get_animal_type_by_id(session=session, type_id=type_id)

    if not animal_type:
        raise HTTPException(status_code=404, detail='Animal type not found')

    return animal_type

def require_breed(breed_id: int, session: Session = Depends(get_db)) -> Breed:
    """Находит породу по id либо кидает 404 - убирает дублирование
    этой проверки в get/update/delete эндпоинтах catalog.py."""
    breed = get_breed_by_id(session=session, breed_id=breed_id)

    if not breed:
        raise HTTPException(status_code=404, detail='Breed not found')

    return breed

def require_animal(animal_id: int, session: Session = Depends(get_db)) -> Animal:
    """Находит животное по id либо кидает 404 - убирает дублирование
    этой проверки в get/update/delete эндпоинтах animals.py."""
    animal = get_animal_by_id(session=session, animal_id=animal_id)

    if not animal:
        raise HTTPException(status_code=404, detail='Animal not found')

    return animal