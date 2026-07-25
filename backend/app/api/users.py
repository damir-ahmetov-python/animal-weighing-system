from fastapi import Depends, APIRouter

from app.schemas import UserResponse
from app.core.deps import get_current_user
from app.models import User

router = APIRouter()

@router.get('/users/me', response_model=UserResponse)
def get_user(user: User = Depends(get_current_user)):
    return user