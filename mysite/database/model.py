from datetime import datetime
from enum import Enum
from typing import List

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from mysite.database.db import Base


class Role(str, Enum):
    student = "student"
    teacher = "teacher"
    manager = "manager"
    admin = "admin"


class Level(str, Enum):
    beginner = "beginner"
    intermediate = "intermediate"
    advanced = "advanced"


class UserStatus(str, Enum):
    free = "free"
    plus = "plus"


class CourseStatus(str, Enum):
    recruiting = "recruiting"
    active = "active"
    completed = "completed"
    cancelled = "cancelled"


class ApplicationStatus(str, Enum):
    new = "new"
    in_progress = "in_progress"
    accepted = "accepted"
    rejected = "rejected"
    cancelled = "cancelled"


class EnrollmentStatus(str, Enum):
    active = "active"
    completed = "completed"
    cancelled = "cancelled"


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    full_name: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(100))
    password: Mapped[str] = mapped_column(String(50), unique=True)
    role: Mapped[Role] = mapped_column(default=Role.student)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime)

    user_groups: Mapped[List["StudyGroup"]] = relationship(
        "StudyGroup",
        back_populates="teacher",
        cascade="all, delete-orphan",
    )


class Category(Base):
    __tablename__ = "category"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    category_name: Mapped[str] = mapped_column(String(50), unique=True)

    category_course: Mapped[List["Course"]] = relationship(
        "Course",
        back_populates="category",
        cascade="all, delete-orphan",
    )


class Course(Base):
    __tablename__ = "course"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(50))
    category_id: Mapped[int] = mapped_column(ForeignKey("category.id"))
    description: Mapped[str] = mapped_column(Text)
    level: Mapped[Level] = mapped_column()
    price: Mapped[int] = mapped_column(Integer)
    duration_weeks: Mapped[int] = mapped_column(Integer)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    status: Mapped[UserStatus] = mapped_column(default=UserStatus.free)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime)

    category: Mapped["Category"] = relationship(
        "Category",
        back_populates="category_course",
    )

    course_group: Mapped[List["StudyGroup"]] = relationship(
        "StudyGroup",
        back_populates="course",
        cascade="all, delete-orphan",
    )


class StudyGroup(Base):
    __tablename__ = "studygroup"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100))
    course_id: Mapped[int] = mapped_column(ForeignKey("course.id"))
    teacher_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    starts_on: Mapped[datetime] = mapped_column(Date)
    ends_on: Mapped[datetime] = mapped_column(Date)
    capacity: Mapped[int] = mapped_column(Integer)
    status: Mapped[CourseStatus] = mapped_column(default=CourseStatus.recruiting)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime)

    course: Mapped["Course"] = relationship(
        "Course",
        back_populates="course_group",
    )

    teacher: Mapped["User"] = relationship(
        "User",
        back_populates="user_groups",
    )


class Application(Base):
    __tablename__ = "application"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    # student_id
    # course_id
    # manager_id
    comment: Mapped[str] = mapped_column(Text)
    status: Mapped[ApplicationStatus] = mapped_column(
        default=ApplicationStatus.in_progress,
    )
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime)


class Enrollment(Base):
    __tablename__ = "enrollment"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    # student_id
    # group_id
    status: Mapped[EnrollmentStatus] = mapped_column(
        default=EnrollmentStatus.active,
    )
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime)