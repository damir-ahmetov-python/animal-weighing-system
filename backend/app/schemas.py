from typing import Literal

from pydantic import BaseModel, EmailStr, ConfigDict, Field, field_validator
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

class AnimalTypeUpdate(BaseModel):
    name_type: str | None = None

class BreedCreate(BaseModel):
    name: str
    type_id: int

class BreedResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    breed_id: int
    name: str
    type_id: int

class BreedUpdate(BaseModel):
    name: str | None = None
    type_id: int | None = None

class AnimalCreate(BaseModel):
    inventory_number: str
    gender: Literal['male', 'female']
    name: str | None = None
    arrival_date: datetime.date
    arrival_age_months: int | None = Field(default=None, ge=0)
    breed_id: int
    parent_id: int | None = None

    @field_validator('arrival_date')
    @classmethod
    def validate_arrival_date(cls, v):
        if v > datetime.date.today():
            raise ValueError('Arrival date cannot be in the future')
        return v

class AnimalUpdate(BaseModel):
    inventory_number: str | None = None
    gender: Literal['male', 'female'] | None = None
    name: str | None = None
    arrival_date: datetime.date | None = None
    arrival_age_months: int | None = Field(default=None, ge=0)
    breed_id: int | None = None
    parent_id: int | None = None

    @field_validator('arrival_date')
    @classmethod
    def validate_arrival_date(cls, v):
        if v is not None and v > datetime.date.today():
            raise ValueError('Arrival date cannot be in the future')
        return v

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

class WeightingCreate(BaseModel):
    animal_id: int
    date: datetime.date
    weight_kg: float = Field(gt=0)

class WeightingUpdate(BaseModel):
    animal_id: int | None = None
    date: datetime.date | None = None
    weight_kg: float | None = Field(gt=0, default=None)

class WeightingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    weighting_id: int
    animal_id: int
    date: datetime.date
    weight_kg: float
    created_by_user_id: int
