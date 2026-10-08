from sqladmin import ModelView

from ..database.model import *


class UserAdmin(ModelView, model=User):
    name = 'User'
    name_plural = 'Users'
    column_list = (
        User.id,
        User.full_name,
        User.email,
        User.created_at,
        User.updated_at
    )

class CategoryAdmin(ModelView, model=Category):
    name = 'Category'
    name_plural = 'Categories'
    column_list = (
        Category.id,
        Category.category_name
    )

class CourseAdmin(ModelView, model=Course):
    name = 'Course'
    name_plural = 'Courses'
    column_list = (
        Course.id,
        Course.title,
        Course.category_id,
        Course.description,
        Course.level,
        Course.price,
        Course.duration_weeks,
        Course.is_active,
        Course.created_at,
        Course.updated_at
    )

class StudyGroupAdmin(ModelView, model=StudyGroup):
    name = 'Study Group'
    name_plural = 'Study Groups'
    column_list = (
        StudyGroup.id,
        StudyGroup.name,
        StudyGroup.course_id,
        StudyGroup.teacher_id,
        StudyGroup.starts_on,
        StudyGroup.ends_on,
        StudyGroup.capacity,
        StudyGroup.status,
        StudyGroup.created_at,
        StudyGroup.updated_at
    )

class ApplicationAdmin(ModelView, model=Application):
    name = 'Application'
    name_plural = 'Applications'
    column_list = (
        Application.id,
        Application.comment,
        Application.status,
        Application.created_at,
        Application.updated_at
    )

class EnrollmentAdmin(ModelView, model=Enrollment):
    name = 'Enrollment'
    name_plural = 'Enrollments'
    column_list = (
        Enrollment.id,
        Enrollment.status,
        Enrollment.created_at,
        Enrollment.updated_at
    )
