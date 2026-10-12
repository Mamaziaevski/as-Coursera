from datetime import date, datetime
from enum import Enum
from typing import List

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
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
    __table_args__ = (UniqueConstraint("email", name="uq_user_email"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    full_name: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(100))
    password: Mapped[str] = mapped_column(String(255), unique=True)
    refresh_token: Mapped[str | None] = mapped_column(String(512), nullable=True)
    role: Mapped[Role] = mapped_column(default=Role.student)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user_groups: Mapped[List["StudyGroup"]] = relationship("StudyGroup", back_populates="teacher", cascade="all, delete-orphan")


class Category(Base):
    __tablename__ = "category"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    category_name: Mapped[str] = mapped_column(String(50), unique=True)

    category_course: Mapped[List["Course"]] = relationship("Course", back_populates="category", cascade="all, delete-orphan")


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
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    category: Mapped["Category"] = relationship("Category", back_populates="category_course")
    teacher_id: Mapped[int] = mapped_column(ForeignKey("user.id", name="fk_course_teacher"))
    course_group: Mapped[List["StudyGroup"]] = relationship("StudyGroup", back_populates="course", cascade="all, delete-orphan")


class StudyGroup(Base):
    __tablename__ = "studygroup"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100))
    course_id: Mapped[int] = mapped_column(ForeignKey("course.id"))
    teacher_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    starts_on: Mapped[date] = mapped_column(Date)
    ends_on: Mapped[date] = mapped_column(Date)
    capacity: Mapped[int] = mapped_column(Integer)
    status: Mapped[CourseStatus] = mapped_column(default=CourseStatus.recruiting)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    course: Mapped["Course"] = relationship(
        "Course",
        back_populates="course_group",
    )

    teacher: Mapped["User"] = relationship("User", back_populates="user_groups")


class Application(Base):
    __tablename__ = "application"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("user.id", name="fk_application_student"))
    course_id: Mapped[int] = mapped_column(ForeignKey("course.id", name="fk_application_course"))
    manager_id: Mapped[int | None] = mapped_column(ForeignKey("user.id", name="fk_application_manager"), nullable=True)
    student: Mapped["User"] = relationship(foreign_keys=[student_id])
    course: Mapped["Course"] = relationship()
    manager: Mapped["User"] = relationship(foreign_keys=[manager_id])
    comment: Mapped[str] = mapped_column(Text)
    status: Mapped[ApplicationStatus] = mapped_column(
        default=ApplicationStatus.new,
    )
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Enrollment(Base):
    __tablename__ = "enrollment"
    __table_args__ = (UniqueConstraint("student_id", "group_id", name="uq_enrollment_student_group"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("user.id", name="fk_enrollment_student"))
    group_id: Mapped[int] = mapped_column(ForeignKey("studygroup.id", name="fk_enrollment_group"))
    student: Mapped["User"] = relationship()
    group: Mapped["StudyGroup"] = relationship()
    status: Mapped[EnrollmentStatus] = mapped_column(
        default=EnrollmentStatus.active,
    )
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)