from datetime import date, datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator
from mysite.database.model import Role, Level, UserStatus, CourseStatus, ApplicationStatus, EnrollmentStatus


class UserBase(BaseModel):
    full_name: str = Field(min_length=1, max_length=50)
    email: EmailStr
    role: Role = Role.student


class UserCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    full_name: str = Field(min_length=1, max_length=50)
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)
    role: Role = Role.student


class UserUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    full_name: str | None = Field(default=None, min_length=1, max_length=50)
    email: EmailStr | None = None
    password: str | None = Field(default=None, min_length=8, max_length=72)
    role: Role | None = None

    @model_validator(mode="after")
    def check_null(self):
        if any(getattr(self, field) is None for field in self.model_fields_set):
            raise ValueError("Переданные поля не могут быть null")
        return self


class UserOutput(UserBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    is_active: bool
    created_at: datetime


class UserLoginSchema(BaseModel):
    email: EmailStr
    password: str = Field(max_length=72)


class TokenResponseSchema(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"


class AccessResponseSchema(BaseModel):
    access_token: str
    token_type: str = "Bearer"


class CategoryCreate(BaseModel):
    category_name: str = Field(min_length=1, max_length=50)


class CategoryOutput(CategoryCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int


class CourseCreate(BaseModel):
    title: str = Field(min_length=1, max_length=50)
    category_id: int = Field(gt=0)
    description: str = Field(min_length=1)
    level: Level = Level.beginner
    price: int = Field(ge=0)
    duration_weeks: int = Field(gt=0)
    is_active: bool = True
    status: UserStatus = UserStatus.free


class CourseOutput(CourseCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    teacher_id: int
    created_at: datetime
    updated_at: datetime


class StudyGroupCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    course_id: int = Field(gt=0)
    starts_on: date
    ends_on: date
    capacity: int = Field(gt=0)
    status: CourseStatus = CourseStatus.recruiting

    @model_validator(mode="after")
    def check_dates(self):
        if self.ends_on < self.starts_on:
            raise ValueError("Дата окончания раньше даты начала")
        return self


class StudyGroupOutput(StudyGroupCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    teacher_id: int
    created_at: datetime
    updated_at: datetime


class ApplicationCreate(BaseModel):
    course_id: int = Field(gt=0)
    comment: str = Field(default="", max_length=2000)


class ApplicationUpdate(BaseModel):
    status: ApplicationStatus
    comment: str | None = Field(default=None, max_length=2000)


class ApplicationOutput(ApplicationCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    student_id: int
    manager_id: int | None
    status: ApplicationStatus
    created_at: datetime
    updated_at: datetime


class EnrollmentCreate(BaseModel):
    group_id: int = Field(gt=0)


class EnrollmentOutput(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    student_id: int
    group_id: int
    status: EnrollmentStatus
    created_at: datetime
    updated_at: datetime


class QuestionSchema(BaseModel):
    question: str = Field(min_length=1, max_length=1000)
