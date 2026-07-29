from typing import List

from fastapi import APIRouter, Depends, HTTPException

from app.schemas import (BreedResponse,
                         BreedUpdate,
                         BreedCreate,
                         AnimalTypeCreate,
                         AnimalTypeResponse,
                         AnimalTypeUpdate
                         )

from app.db.session import get_db
from app.db.crud import (get_animal_type_by_id,
                         create_breed,
                         get_all_breeds,
                         delete_breed,
                         create_animal_type,
                         get_all_animal_types,
                         delete_animal_type,
                         update
                         )

from sqlalchemy.exc import IntegrityError
from app.models import AnimalType, Breed
from app.core.deps import get_current_user, require_animal_type, require_breed

from sqlalchemy.orm import Session

router = APIRouter(dependencies=[Depends(get_current_user)])

@router.post("/animal_types", response_model=AnimalTypeResponse, tags=["animal_types"])
def create_animal_type_endpoint(
        animal_type_data: AnimalTypeCreate,
        session: Session = Depends(get_db)
):
    """IntegrityError здесь означает дубликат name_type (unique-констрейнт в БД)."""
    try:
        animal_type = create_animal_type(session=session, name_type=animal_type_data.name_type)
        return animal_type
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=409, detail='Animal type already exists')

@router.get("/animal_types", response_model=List[AnimalTypeResponse], tags=["animal_types"])
def get_animal_types(session: Session = Depends(get_db)):
    return get_all_animal_types(session=session)

@router.get("/animal_types/{type_id}", response_model=AnimalTypeResponse, tags=["animal_types"])
def get_animal_type(type_id: int, animal_type: AnimalType = Depends(require_animal_type)):
    return animal_type

@router.patch("/animal_types/{type_id}", response_model=AnimalTypeResponse, tags=["animal_types"])
def update_animal_type_endpoint(
        type_id: int,
        data: AnimalTypeUpdate,
        session: Session = Depends(get_db),
        animal_type: AnimalType = Depends(require_animal_type)
):
    # exclude_unset - чтобы не затирать нетронутые поля значениями по умолчанию
    update_data = data.model_dump(exclude_unset=True)

    try:
        return update(session=session, obj=animal_type, data=update_data)
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=409, detail='Animal type with this name already exists')

@router.delete("/animal_types/{type_id}", response_model=bool, tags=["animal_types"])
def delete_animal_type_endpoint(
        type_id: int,
        session: Session = Depends(get_db),
        animal_type: AnimalType = Depends(require_animal_type)
):
    # IntegrityError - на этот type_id ссылается хотя бы один breed (FK RESTRICT)
    try:
        delete_animal_type(session=session, animal_type=animal_type)

        return True
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=409, detail='Cannot delete: animal type is referenced by existing breeds')

@router.post("/breeds", response_model=BreedResponse, tags=["breeds"])
def create_breed_endpoint(
        breed_data: BreedCreate,
        session: Session = Depends(get_db)
):
    """Проверка type_id заранее - чтобы 404 (нет такого типа) не терялось
    за общим 409 от FK, если IntegrityError мог бы прилететь по двум причинам сразу."""
    if not get_animal_type_by_id(session=session, type_id=breed_data.type_id):
        raise HTTPException(status_code=404, detail='Animal type not found')

    try:
        breed = create_breed(session=session, name=breed_data.name, type_id=breed_data.type_id)

        return breed
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=409, detail='Data conflict: check animal type reference and breed name uniqueness')

@router.get("/breeds", response_model=List[BreedResponse], tags=["breeds"])
def get_breeds(session: Session = Depends(get_db)):
    return get_all_breeds(session=session)

@router.get("/breeds/{breed_id}", response_model=BreedResponse, tags=["breeds"])
def get_breed(breed_id: int, breed: Breed = Depends(require_breed)):
    return breed

@router.patch("/breeds/{breed_id}", response_model=BreedResponse, tags=["breeds"])
def update_breed_endpoint(
        breed_id: int,
        data: BreedUpdate,
        session: Session = Depends(get_db),
        breed: Breed = Depends(require_breed)
):
    update_data = data.model_dump(exclude_unset=True)

    # type_id меняют не всегда - проверяем ссылку только если её реально прислали
    if 'type_id' in update_data and not get_animal_type_by_id(session=session, type_id=update_data['type_id']):
        raise HTTPException(status_code=404, detail='Animal type not found')

    try:
        return update(session=session, obj=breed, data=update_data)
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=409, detail='Data conflict: check animal type reference and breed name uniqueness')

@router.delete("/breeds/{breed_id}", response_model=bool, tags=["breeds"])
def delete_breed_endpoint(
        breed_id: int,
        session: Session = Depends(get_db),
        breed: Breed = Depends(require_breed)
):
    # IntegrityError - на эту породу ссылается хотя бы один animal (FK RESTRICT)
    try:
        delete_breed(session=session, breed=breed)
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=409, detail='Cannot delete: breed is referenced by existing animals')

    return True

