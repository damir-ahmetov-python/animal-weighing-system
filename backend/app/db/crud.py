import datetime

from app.models import User, AnimalType, Breed, Animal
from sqlalchemy import select
from sqlalchemy.orm import Session

def create_user(
        session: Session,
        login: str,
        email: str,
        hashed_password: str,
        activation_token: str | None = None
) -> User:

    user = User(
        login=login,
        email=email,
        hashed_password=hashed_password,
        activation_token=activation_token,
    )

    session.add(user)

    session.commit()
    session.refresh(user)

    return user


def get_by_email(session: Session, email: str) -> User | None:
    res = session.execute(select(User).where(User.email == email))

    return res.scalar_one_or_none()


def get_by_login(session: Session, login: str) -> User | None:
    res = session.execute(select(User).where(User.login == login))

    return res.scalar_one_or_none()


def get_by_id(session: Session, user_id: int) -> User | None:
    res = session.execute(select(User).where(User.id == user_id))

    return res.scalar_one_or_none()

def get_by_activation_token(session: Session, token: str) -> User | None:
    res = session.execute(select(User).where(User.activation_token == token))

    return res.scalar_one_or_none()

def create_animal_type(session: Session, name_type: str) -> AnimalType:
    animal_type = AnimalType(name_type=name_type)

    session.add(animal_type)

    session.commit()
    session.refresh(animal_type)

    return animal_type

def get_animal_type_by_id(session: Session, type_id: int) -> AnimalType | None:
    res = session.execute(select(AnimalType).where(AnimalType.type_id == type_id))

    return res.scalar_one_or_none()

def get_animal_type_by_name(session: Session, name_type: str) -> AnimalType | None:
    res = session.execute(select(AnimalType).where(AnimalType.name_type == name_type))

    return res.scalar_one_or_none()

def get_all_animal_types(session: Session) -> list[AnimalType]:
    res = session.execute(select(AnimalType))
    return list(res.scalars().all())

def update_animal_type(session: Session, animal_type: AnimalType, data: dict) -> AnimalType:
    for k, v in data.items():
        setattr(animal_type, k, v)

    session.commit()
    session.refresh(animal_type)

    return animal_type

def delete_animal_type(session: Session, animal_type: AnimalType) -> None:
    session.delete(animal_type)
    session.commit()

def create_breed(session: Session, name: str, type_id: int) -> Breed:
    breed = Breed(name=name, type_id=type_id)

    session.add(breed)

    session.commit()
    session.refresh(breed)

    return breed

def get_breed_by_id(session: Session, breed_id: int) -> Breed | None:
    res = session.execute(select(Breed).where(Breed.breed_id == breed_id))

    return res.scalar_one_or_none()

def get_all_breeds(session: Session) -> list[Breed]:
    res = session.execute(select(Breed))
    return list(res.scalars().all())

def update_breed(session: Session, breed: Breed, data: dict) -> Breed:
    for k, v in data.items():
        setattr(breed, k, v)

    session.commit()
    session.refresh(breed)

    return breed

def delete_breed(session: Session, breed: Breed) -> None:
    session.delete(breed)
    session.commit()

def create_animal(
        session: Session,
        inventory_number: str,
        gender: str,
        name: str,
        arrival_date: datetime.date,
        arrival_age_months: int,
        breed_id: int,
        parent_id: int | None = None
) -> Animal:

    animal = Animal(
        inventory_number=inventory_number,
        gender=gender,
        name=name,
        arrival_date=arrival_date,
        arrival_age_months=arrival_age_months,
        breed_id=breed_id,
        parent_id=parent_id,
    )

    session.add(animal)

    session.commit()
    session.refresh(animal)

    return animal

def get_animal_by_id(session: Session, animal_id: int) -> Animal | None:
    res = session.execute(select(Animal).where(Animal.animal_id == animal_id))

    return res.scalar_one_or_none()

def get_all_animals(session: Session) -> list[Animal]:
    res = session.execute(select(Animal))

    return list(res.scalars().all())

def update_animal(session: Session, animal: Animal, data: dict) -> Animal:
    for k, v in data.items():
        setattr(animal, k, v)

    session.commit()
    session.refresh(animal)

    return animal

def delete_animal(session: Session, animal: Animal) -> None:
    session.delete(animal)
    session.commit()


