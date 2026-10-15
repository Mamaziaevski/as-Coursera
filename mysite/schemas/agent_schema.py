from typing import Literal
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from mysite.schemas.answer_format import single_line_answer


# Входной текст из Postman.
class AgentInputSchema(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    message: str = Field(min_length=1, max_length=4000)


# Текстовый ответ агента.
class AgentOutputSchema(BaseModel):
    answer: str

    @field_validator('answer')
    @classmethod
    def format_answer(cls, value: str) -> str:
        return single_line_answer(value)


# Чтение и удаление не принимают user_id.
class EmptyToolSchema(BaseModel):
    # Если модель передаст user_id=999, проверка отвергнет лишнее поле.
    model_config = ConfigDict(extra="forbid")


# Поля нового аккаунта.
class UserRegisterInputSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")
    full_name: str = Field(min_length=1, max_length=50)
    email: EmailStr = Field(max_length=100)
    password: str = Field(min_length=8, max_length=72)
    # Через публичного агента нельзя зарегистрироваться администратором.
    role: Literal["student"] = "student"
    is_active: bool = True


# Передавать только новые значения полей.
class UserUpdateInputSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")
    full_name: str | None = Field(default=None, min_length=1, max_length=50)
    email: EmailStr | None = Field(default=None, max_length=100)
    password: str | None = Field(default=None, min_length=8, max_length=72)

