from datetime import timezone
from fastapi import HTTPException
from pydantic import ValidationError
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from mysite.api.auth import hash_password
from mysite.database.model import Application, Course, Enrollment, Role, StudyGroup, User
from mysite.database.schema import UserOutput, UserUpdate
from agent_style.schemas.agent_schema import EmptyToolSchema, UserRegisterInputSchema, UserUpdateInputSchema


# Схема аргументов каждого инструмента.
tool_schemas = {
    "get_my_profile": EmptyToolSchema,
    "update_my_profile": UserUpdateInputSchema,
    "delete_my_profile": EmptyToolSchema,
    "register_user": UserRegisterInputSchema,
}


# Объяснение функций для модели.
tool_descriptions = {
    "get_my_profile": "Прочитать профиль текущего пользователя: ФИО, email, роль, id, created_at, is_active. Без аргументов. Чужие профили недоступны.",
    "update_my_profile": "Изменить только свой профиль. Передавай только явно названные новые full_name, email, password. Роль и id менять нельзя.",
    "delete_my_profile": "Удалить свой аккаунт, только если пользователь явно попросил удалить его. Без аргументов. Связанный с учебными записями аккаунт удалить нельзя.",
    "register_user": "Создать новый аккаунт student. Нужны full_name, email, password. Не выдумывай недостающие значения: спроси пользователя. is_active по умолчанию true.",
}


# JSON-описания инструментов для Ollama.
def get_tools(names: list[str]) -> list[dict]:
    return [
        {
            "type": "function",
            "function": {
                "name": name,
                "description": tool_descriptions[name],
                "parameters": tool_schemas[name].model_json_schema(),
            },
        }
        for name in names
    ]


# Профиль без пароля и токенов; дата в UTC.
def user_profile_data(current_user: User) -> dict:
    data = UserOutput.model_validate(current_user).model_dump(mode="json")
    created_at = current_user.created_at
    # В текущей модели datetime.utcnow хранится без tzinfo, но означает UTC.
    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc)
    data["created_at"] = created_at.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    return data


# Чтение своего профиля.
async def get_my_profile(db: AsyncSession, current_user: User) -> dict:
    return {"profile": user_profile_data(current_user)}


# Обновление своего профиля; пароль сохраняется хешем.
async def update_my_profile(db: AsyncSession, current_user: User, data: UserUpdateInputSchema) -> dict:
    # Повторно используем UserUpdate: он запрещает явно переданные null.
    changes = UserUpdate.model_validate(data.model_dump(exclude_unset=True))
    values = changes.model_dump(exclude_unset=True)
    if not values:
        raise HTTPException(status_code=422, detail="Укажи хотя бы одно поле для изменения")
    password = values.pop("password", None)
    for field, value in values.items():
        setattr(current_user, field, str(value).lower() if field == "email" else value)
    if password is not None:
        current_user.password = hash_password(password)
        current_user.refresh_token = None
    # flush отправляет изменения в БД, но ещё не завершает транзакцию.
    await db.flush()
    await db.refresh(current_user)
    return {"message": "Профиль обновлён", "profile": user_profile_data(current_user)}


# Перед удалением проверяем учебные связи.
async def delete_my_profile(db: AsyncSession, current_user: User) -> dict:
    # Проверяем связи заранее: ORM содержит cascade и мог бы удалить группы вместе с человеком.
    checks = [
        select(Course.id).where(Course.teacher_id == current_user.id),
        select(StudyGroup.id).where(StudyGroup.teacher_id == current_user.id),
        select(Application.id).where(or_(Application.student_id == current_user.id, Application.manager_id == current_user.id)),
        select(Enrollment.id).where(Enrollment.student_id == current_user.id),
    ]
    for query in checks:
        if (await db.scalar(query.limit(1))) is not None:
            raise HTTPException(status_code=409, detail="Аккаунт связан с курсами, группами, заявками или зачислениями")
    await db.delete(current_user)
    await db.flush()
    return {"message": "Свой аккаунт удалён", "deleted": True}


# Регистрация нового пользователя student.
async def register_user(db: AsyncSession, data: UserRegisterInputSchema) -> dict:
    email = str(data.email).lower()
    if (await db.scalar(select(User.id).where(User.email == email))) is not None:
        raise HTTPException(status_code=409, detail="Этот email уже зарегистрирован")
    user_db = User(
        full_name=data.full_name,
        email=email,
        password=hash_password(data.password),
        role=Role.student,
        is_active=data.is_active,
    )
    db.add(user_db)
    await db.flush()
    await db.refresh(user_db)
    return {"message": "Регистрация успешна", "profile": user_profile_data(user_db)}


# Проверка названия инструмента и его аргументов.
async def execute_tool(name: str, arguments: dict, db: AsyncSession, current_user: User | None, allowed: list[str]) -> dict:
    if name not in allowed or name not in tool_schemas:
        raise HTTPException(status_code=502, detail="Модель запросила недоступный инструмент")
    try:
        data = tool_schemas[name].model_validate(arguments)
        if name == "register_user":
            return await register_user(db, data)
        if current_user is None:
            raise HTTPException(status_code=401, detail="Not authenticated")
        if name == "get_my_profile":
            return await get_my_profile(db, current_user)
        if name == "update_my_profile":
            return await update_my_profile(db, current_user, data)
        return await delete_my_profile(db, current_user)
    except ValidationError:
        # Не возвращаем str(exc): он может содержать переданный пароль.
        raise HTTPException(status_code=422, detail="Некорректные аргументы инструмента: проверь поля, email и пароль") from None
