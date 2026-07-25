import datetime
from sqlalchemy import String, Integer, Date, Float, Enum, ForeignKey, UniqueConstraint, DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass

class User(Base):
    """Данные о пользователе системы (обычный пользователь или администратор)."""

    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    login: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(128), nullable=False)
    is_active: Mapped[bool] = mapped_column(default=False)
    activation_token: Mapped[str | None] = mapped_column(String(64), nullable=True)

    role: Mapped[str] = mapped_column(
        Enum('user', 'admin', name='user_role_enum'),
        nullable=False,
        default='user'
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    weightings: Mapped[list["Weighting"]] = relationship(back_populates="created_by")

class AnimalType(Base):
    """Тип животного (корова, лошадь и т.п.)."""

    __tablename__ = 'animaltype'

    type_id: Mapped[int] = mapped_column(primary_key=True)
    name_type: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)

    breeds: Mapped[list["Breed"]] = relationship(back_populates="animaltype", passive_deletes=True)


class Breed(Base):
    """Порода животного с привязкой к типу животного."""

    __tablename__ = 'breed'

    breed_id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)

    type_id: Mapped[int] = mapped_column(ForeignKey('animaltype.type_id'), nullable=False)

    animaltype: Mapped["AnimalType"] = relationship(back_populates="breeds")
    animals: Mapped[list["Animal"]] = relationship(back_populates="breed", passive_deletes=True)

class Animal(Base):
    """Данные о животном: инвентарный номер, пол, кличка, дата прибытия, возраст, порода и родитель."""

    __tablename__ = 'animal'

    animal_id: Mapped[int] = mapped_column(primary_key=True)
    inventory_number: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, index=True
    )
    gender: Mapped[str] = mapped_column(
        Enum('male', 'female', name='gender_enum'), nullable=False
    )
    name: Mapped[str] = mapped_column(String(100), nullable=True)  # кличка может отсутствовать
    arrival_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    arrival_age_months: Mapped[int] = mapped_column(Integer, nullable=True)

    breed_id: Mapped[int] = mapped_column(ForeignKey('breed.breed_id'), nullable=True)
    parent_id: Mapped[int] = mapped_column(
        ForeignKey('animal.animal_id', ondelete='SET NULL'), nullable=True
    )  # ссылка на самого себя (родитель)

    breed: Mapped["Breed"] = relationship(back_populates="animals")
    # Для родителя (self-reference)
    parent: Mapped["Animal"] = relationship(
        remote_side=[animal_id], back_populates="children"
    )
    children: Mapped[list["Animal"]] = relationship(back_populates="parent")
    weightings: Mapped[list["Weighting"]] = relationship(back_populates="animal")


class Weighting(Base):
    """Данные о взвешивании животного: дата и вес в кг (уникально для животного и даты)."""

    __tablename__ = 'weighting'

    weighting_id: Mapped[int] = mapped_column(primary_key=True)
    animal_id: Mapped[int] = mapped_column(
        ForeignKey('animal.animal_id'), nullable=False
    )
    date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    weight_kg: Mapped[float] = mapped_column(Float, nullable=False)
    created_by_user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)

    animal: Mapped["Animal"] = relationship(back_populates="weightings")
    created_by: Mapped["User"] = relationship(back_populates="weightings")

    # Ограничение: уникальная пара (animal_id, date)
    __table_args__ = (
        UniqueConstraint('animal_id', 'date', name='uq_animal_weighting_date'),
    )