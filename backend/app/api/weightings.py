from typing import List

from fastapi import APIRouter, Depends, HTTPException

from app.schemas import WeightingCreate, WeightingUpdate, WeightingResponse
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models import User, Weighting
from app.core.deps import get_current_user, get_weighting
from app.db.crud import (create_weighting,
                         get_all_weightings,
                         get_weighting_by_user,
                         update_weighting,
                         delete_weighting,
                         get_animal_by_id
                         )

router = APIRouter(prefix="/weightings", tags=["weightings"])

@router.post("", response_model=WeightingResponse)
def create_weighting_endpoint(
        weighting_data: WeightingCreate,
        session: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    if not get_animal_by_id(session=session, animal_id=weighting_data.animal_id):
        raise HTTPException(status_code=404, detail='Animal not found')

    try:
        weighting = create_weighting(
            session=session,
            animal_id=weighting_data.animal_id,
            date=weighting_data.date,
            weight_kg=weighting_data.weight_kg,
            created_by_user_id=current_user.id
        )

        return weighting
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=409, detail="Weighting already exist")

@router.get("", response_model=List[WeightingResponse])
def get_weightings(session: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role == "admin":
        return get_all_weightings(session=session)
    else:
        return get_weighting_by_user(session=session, user_id=current_user.id)

@router.get("/{weighting_id}", response_model=WeightingResponse)
def get_weighting_endpoint(
        weighting_id: int,
        session: Session = Depends(get_db),
        weighting: Weighting = Depends(get_weighting)
):
    return weighting

@router.patch("/{weighting_id}", response_model=WeightingResponse)
def update_weighting_endpoint(
        weighting_id: int,
        data: WeightingUpdate,
        session: Session = Depends(get_db),
        weighting: Weighting = Depends(get_weighting)
):
    update_data = data.model_dump(exclude_unset=True)

    if 'animal_id' in update_data and not get_animal_by_id(session=session, animal_id=update_data['animal_id']):
        raise HTTPException(status_code=404, detail='Animal not found')

    try:
        return update_weighting(session=session, weighting=weighting, data=update_data)
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=409, detail='Data conflict')


@router.delete("/{weighting_id}", response_model=bool)
def delete_weighting_endpoint(
        weighting_id: int,
        session: Session = Depends(get_db),
        weighting: Weighting = Depends(get_weighting)
):
    delete_weighting(session=session, weighting=weighting)

    return True
