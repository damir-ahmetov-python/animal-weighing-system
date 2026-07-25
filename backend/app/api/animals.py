from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.schemas import AnimalCreate, AnimalResponse, AnimalUpdate
from app.db.session import get_db
from app.db.crud import get_animal_by_id, update_animal, create_animal
from app.models import User
from app.core.deps import get_current_user

router = APIRouter(prefix='/animals', tags=["animals"])

@router.post("/create", response_model=AnimalResponse)
def create_animal_endpoint(animal_data: AnimalCreate, session: Session = Depends(get_db)):
    animal = create_animal(
        session=session,
        inventory_number=animal_data.inventory_number,
        gender=animal_data.gender,
        name=animal_data.name,
        arrival_date=animal_data.arrival_date,
        arrival_age_months=animal_data.arrival_age_months,
        breed_id=animal_data.breed_id,
        parent_id=animal_data.parent_id,
    )

    return animal

@router.get("", response_model=List[AnimalResponse])
def get_animals(session: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    pass

@router.get("/{animal_id}", response_model=AnimalResponse)
def get_animal(animal_id: int, session: Session = Depends(get_db)):
    animal = get_animal_by_id(session=session, animal_id=animal_id)

    if not animal:
        raise HTTPException(status_code=404, detail='Animal not found')

    return animal

@router.delete("/{animal_id}", response_model=bool)
def delete_animal(animal_id: int, session: Session = Depends(get_db)):
    pass

@router.patch("/{animal_id}", response_model=AnimalResponse)
def update_animal_endpoint(animal_id: int, data: AnimalUpdate, session: Session = Depends(get_db)):
    animal = get_animal_by_id(session=session, animal_id=animal_id)

    if not animal:
        raise HTTPException(status_code=404, detail='Animal not found')

    update_data = data.model_dump(exclude_unset=True)

    try:
        return update_animal(session=session, animal=animal, data=update_data)
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=409, detail='Inventory number already exists')