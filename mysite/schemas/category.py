from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from mysite.database.db import get_db
from mysite.database.model import Category
from mysite.database.schema import CategoryCreate, CategoryOutput
from mysite.database.model import Course
from mysite.permissions import get_admin

router = APIRouter(prefix="/categories", tags=["Categories"], dependencies=[Depends(get_admin)])

@router.get("/", response_model=list[CategoryOutput])
async def category_list(db: AsyncSession = Depends(get_db)):
    result = await db.scalars(select(Category).order_by(Category.id))
    return list(result.all())

@router.get("/{category_id}/", response_model=CategoryOutput)
async def category_detail(category_id: int, db: AsyncSession = Depends(get_db)):
    category = await db.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category

@router.post("/", response_model=CategoryOutput, status_code=201)
async def category_create(data: CategoryCreate, db: AsyncSession = Depends(get_db)):
    category = Category(**data.model_dump())
    db.add(category)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail="Такая категория уже есть")
    await db.refresh(category)
    return category


@router.put("/{category_id}/", response_model=CategoryOutput)
async def category_update(category_id: int, data: CategoryCreate, db: AsyncSession = Depends(get_db)):
    category = await category_detail(category_id, db)
    category.category_name = data.category_name
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail="Такая категория уже есть")
    await db.refresh(category)
    return category


@router.delete("/{category_id}/", status_code=200)
async def category_delete(category_id: int, db: AsyncSession = Depends(get_db)):
    category = await category_detail(category_id, db)

    if await db.scalar(select(Course.id).where(Course.category_id == category_id)):
        raise HTTPException(status_code=409, detail="Сначала удалите курсы категории")

    await db.delete(category)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail="Категория используется в курсах")

    return {"message": "Категория успешно удалена"}
