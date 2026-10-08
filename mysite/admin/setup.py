from fastapi import FastAPI
from sqladmin import Admin

from .views import *
from mysite.database.db import engine


def setup_admin(app: FastAPI) -> None:
    admin = Admin(app=app, engine=engine, title="Order")
    admin.add_view(UserAdmin)
    admin.add_view(CategoryAdmin)
    admin.add_view(CourseAdmin)
    admin.add_view(StudyGroupAdmin)
    admin.add_view(ApplicationAdmin)
    admin.add_view(EnrollmentAdmin)