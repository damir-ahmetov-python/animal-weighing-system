from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.schemas import AnimalCreate, AnimalResponse, AnimalUpdate
from app.db.session import get_db
from app.db.crud import get_animal_by_id, update_animal, create_animal, delete_animal, get_all_animals, get_breed_by_id
from app.models import User
from app.core.deps import get_current_user

router = APIRouter(prefix='/animals', tags=["animals"])

@router.post("", response_model=AnimalResponse)
def create_animal_endpoint(animal_data: AnimalCreate, session: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not get_breed_by_id(session=session, breed_id=animal_data.breed_id):
        raise HTTPException(status_code=404, detail='Breed not found')

    if animal_data.parent_id is not None and not get_animal_by_id(session=session, animal_id=animal_data.parent_id):
        raise HTTPException(status_code=404, detail='Parent animal not found')

    try:
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
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=409, detail='Data conflict: check inventory number, breed and parent references')

@router.get("", response_model=List[AnimalResponse])
def get_animals(session: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return get_all_animals(session=session)

@router.get("/{animal_id}", response_model=AnimalResponse)
def get_animal(animal_id: int, session: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    animal = get_animal_by_id(session=session, animal_id=animal_id)

    if not animal:
        raise HTTPException(status_code=404, detail='Animal not found')

    return animal

@router.patch("/{animal_id}", response_model=AnimalResponse)
def update_animal_endpoint(animal_id: int, data: AnimalUpdate, session: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    animal = get_animal_by_id(session=session, animal_id=animal_id)

    if not animal:
        raise HTTPException(status_code=404, detail='Animal not found')

    update_data = data.model_dump(exclude_unset=True)

    if 'breed_id' in update_data and not get_breed_by_id(session=session, breed_id=update_data['breed_id']):
        raise HTTPException(status_code=404, detail='Breed not found')

    if update_data.get('parent_id') is not None and not get_animal_by_id(session=session, animal_id=update_data['parent_id']):
        raise HTTPException(status_code=404, detail='Parent animal not found')

    try:
        return update_animal(session=session, animal=animal, data=update_data)
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=409, detail='Data conflict: check inventory number, breed and parent references')

@router.delete("/{animal_id}", response_model=bool)
def delete_animal_endpoint(animal_id: int, session: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    animal = get_animal_by_id(session=session, animal_id=animal_id)

    if not animal:
        raise HTTPException(status_code=404, detail='Animal not found')

    try:
        delete_animal(session=session, animal=animal)
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=409, detail='Cannot delete: animal is referenced by existing weighing records')

    return True
