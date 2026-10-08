from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from mysite.api.auth import get_current_user, hash_password
from mysite.database.db import get_db
from mysite.database.model import User
from mysite.database.schema import UserOutput, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=list[UserOutput])
async def list_users(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
) -> list[User]:
    result = await db.scalars(select(User).order_by(User.id))
    return list(result.all())


@router.get("/{user_id}", response_model=UserOutput)
async def user_detail(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
) -> User:
    user = await db.get(User, user_id)
    if user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")
    return user


@router.patch("/{user_id}", response_model=UserOutput)
async def update_user(
    user_id: int,
    data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> User:
    if current_user.id != user_id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "You can update only your own profile")
    values = data.model_dump(exclude_unset=True)
    password = values.pop("password", None)
    if "email" in values and values["email"] is not None:
        values["email"] = str(values["email"]).lower()
    for field, value in values.items():
        setattr(current_user, field, value)
    if password:
        current_user.password = hash_password(password)
    try:
        await db.commit()
    except IntegrityError as exc:
        await db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, "Email already exists") from exc
    await db.refresh(current_user)
    return current_user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Response:
    if current_user.id != user_id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "You can delete only your own profile")
    await db.delete(current_user)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


