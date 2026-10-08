from sqladmin import ModelView

from ..database.models import *


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

