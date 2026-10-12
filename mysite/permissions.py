from fastapi import Depends, HTTPException
from mysite.api.auth import get_current_user
from mysite.database.model import User, Course, Role, UserStatus


def check_role(user: User, role: Role):
    if user.role != role:
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    return user


async def get_admin(current_user: User = Depends(get_current_user)):
    return check_role(current_user, Role.admin)


async def get_teacher(current_user: User = Depends(get_current_user)):
    return check_role(current_user, Role.teacher)


async def get_manager(current_user: User = Depends(get_current_user)):
    return check_role(current_user, Role.manager)


async def get_student(current_user: User = Depends(get_current_user)):
    return check_role(current_user, Role.student)


def check_course_owner(course: Course, current_user: User):
    if course.teacher_id != current_user.id:
        raise HTTPException(status_code=403, detail="Можно изменять только свой курс")


def check_course_access(course: Course, current_user: User):
    if not course.is_active:
        raise HTTPException(status_code=409, detail="Курс недоступен")
    if not current_user.is_active and course.status == UserStatus.plus:
        raise HTTPException(status_code=403, detail="Этот курс доступен только с plus")
