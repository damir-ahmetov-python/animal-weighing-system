from typing import List

from fastapi import APIRouter, Depends, HTTPException
from app.core.deps import require_admin
from app.schemas import UserResponse
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.crud import get_all_users, get_by_id, update_user_toggle_active

router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(require_admin)])

@router.get("/users", response_model=List[UserResponse])
def get_users(session: Session = Depends(get_db)):
    """Доступ только admin - проверяется через require_admin на уровне роутера."""
    return get_all_users(session=session)

@router.patch("/users/{user_id}/toggle-active", response_model=UserResponse)
def update_user_toggle_active_endpoint(user_id: int, session: Session = Depends(get_db)):
    """Включает/отключает пользователя (is_active) - неактивный не может логиниться."""
    user = get_by_id(session=session, user_id=user_id)

    if not user:
        raise HTTPException(status_code=404, detail='User not found')

    return update_user_toggle_active(session=session, user=user)