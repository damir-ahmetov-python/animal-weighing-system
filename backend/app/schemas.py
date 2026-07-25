from typing import Literal

from pydantic import BaseModel, EmailStr, ConfigDict, Field
import datetime

class UserCreate(BaseModel):
    login: str
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    login: str | None
    email: str
    is_active: bool
    role: str
    created_at: datetime.datetime

class Token(BaseModel):
    access_token: str
    token_type: str

class AnimalTypeCreate(BaseModel):
    name_type: str

class AnimalTypeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    type_id: int
    name_type: str

class BreedCreate(BaseModel):
    name: str
    type_id: int

class BreedResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    breed_id: int
    name: str

class AnimalCreate(BaseModel):
    inventory_number: str
    gender: Literal['male', 'female']
    name: str | None = None
    arrival_date: datetime.date
    arrival_age_months: int | None = None
    breed_id: int
    parent_id: int | None = None

class AnimalUpdate(BaseModel):
    inventory_number: str | None = None
    gender: Literal['male', 'female'] | None = None
    name: str | None = None
    arrival_date: datetime.date | None = None
    arrival_age_months: int | None = None
    breed_id: int | None = None
    parent_id: int | None = None

class AnimalResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    animal_id: int
    inventory_number: str
    gender: Literal['male', 'female']
    name: str | None = None
    arrival_date: datetime.date
    arrival_age_months: int | None = None
    breed_id: int
    parent_id: int | None = None

