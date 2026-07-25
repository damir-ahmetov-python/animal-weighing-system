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
    weightings: list

class Token(BaseModel):
    access_token: str
    token_type: str