import datetime

from app.models import User, AnimalType, Breed, Animal, Weighting
from sqlalchemy import select
from sqlalchemy.orm import Session


def _get_all(session: Session, model) -> list:
    """Общий паттерн для get_all_: без фильтров, весь список сущностей."""
    return list(session.execute(select(model)).scalars().all())


def update(session: Session, obj, data: dict):
    """Общая CRUD-операция частичного обновления: применяет только присланные
    поля (data - результат model_dump(exclude_unset=True) на стороне роутера)
    к уже полученному объекту (AnimalType/Breed/Animal/Weighting)."""
    for k, v in data.items():
        setattr(obj, k, v)

    session.commit()
    session.refresh(obj)

    return obj


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
    """Ищет пользователя по email - используется при регистрации, чтобы
    отсечь дубликат ещё до попытки вставки в БД."""
    res = session.execute(select(User).where(User.email == email))

    return res.scalar_one_or_none()


def get_by_login(session: Session, login: str) -> User | None:
    """Ищет пользователя по login - используется при регистрации и логине."""
    res = session.execute(select(User).where(User.login == login))

    return res.scalar_one_or_none()


def get_by_id(session: Session, user_id: int) -> User | None:
    res = session.execute(select(User).where(User.id == user_id))

    return res.scalar_one_or_none()

def get_by_activation_token(session: Session, token: str) -> User | None:
    """Ищет пользователя по одноразовому токену активации из ссылки в письме."""
    res = session.execute(select(User).where(User.activation_token == token))

    return res.scalar_one_or_none()

def get_all_users(session: Session) -> list[User]:
    return _get_all(session, User)

def update_user_toggle_active(session: Session, user: User) -> User:
    """Переключает is_active на противоположное значение (вкл/выкл юзера админом)."""
    user.is_active = not user.is_active

    session.commit()
    session.refresh(user)

    return user

def activate_user(session: Session, user: User) -> User:
    """Активирует пользователя и очищает одноразовый токен активации."""
    user.is_active = True
    user.activation_token = None

    session.commit()
    session.refresh(user)

    return user

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
    return _get_all(session, AnimalType)

def delete_animal_type(session: Session, animal_type: AnimalType) -> None:
    """Удаляет тип животного. Если на него ссылаются breed - БД сама вернёт
    IntegrityError (RESTRICT), роутер поймает и превратит в 409."""
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
    return _get_all(session, Breed)

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
    return _get_all(session, Animal)

def delete_animal(session: Session, animal: Animal) -> None:
    """Удаляет животное. Если на него ссылается weighting - IntegrityError,
    роутер вернёт 409."""
    session.delete(animal)
    session.commit()

def create_weighting(
        session: Session,
        animal_id: int,
        date: datetime.date,
        weight_kg:float,
        created_by_user_id: int
) -> Weighting:
    """created_by_user_id приходит из current_user на стороне роутера,
    а не из тела запроса - иначе юзер мог бы приписать запись кому угодно."""
    weighting = Weighting(
        animal_id=animal_id,
        date=date,
        weight_kg=weight_kg,
        created_by_user_id=created_by_user_id
    )

    session.add(weighting)

    session.commit()
    session.refresh(weighting)

    return weighting


def get_weighting_by_id(session: Session, weighting_id: int) -> Weighting | None:
    res = session.execute(select(Weighting).where(Weighting.weighting_id == weighting_id))

    return res.scalar_one_or_none()

def get_all_weightings(session: Session) -> list[Weighting]:
    """Для admin - все записи без фильтра по владельцу."""
    return _get_all(session, Weighting)

def get_weighting_by_user(session: Session, user_id: int) -> list[Weighting]:
    """Для обычного юзера - только записи, которые он сам создал."""
    res = session.execute(select(Weighting).where(Weighting.created_by_user_id == user_id))

    return list(res.scalars().all())


def delete_weighting(session: Session, weighting: Weighting) -> None:
    # нет try/except как в delete_animal/delete_breed/delete_animal_type -
    # на weighting никто не ссылается по FK, IntegrityError здесь недостижим
    session.delete(weighting)
    session.commit()
