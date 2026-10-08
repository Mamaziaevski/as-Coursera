from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from mysite.database.model import Role


class UserBase(BaseModel):
    full_name: str = Field(min_length=1, max_length=100)
    email: EmailStr | None = None
    role: Role = Role.student


class UserCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    full_name: str = Field(min_length=1, max_length=50)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    role: Role = Role.student


class UserUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=1, max_length=100)
    email: EmailStr | None = None
    password: str | None = Field(default=None, min_length=8, max_length=128)
    role: Role | None = None


class UserOutput(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    registered_date: datetime


class UserLoginSchema(BaseModel):
    email: EmailStr
    password: str


class TokenResponseSchema(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"


class AccessResponseSchema(BaseModel):
    access_token: str
    token_type: str = "Bearer"
