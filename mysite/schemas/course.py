from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from mysite.database.db import get_db
from mysite.database.model import Category, Course, StudyGroup, Application, User
from mysite.database.schema import CourseCreate, CourseOutput
from mysite.permissions import get_teacher, check_course_owner

router = APIRouter(prefix="/courses", tags=["Courses"])


@router.get("/", response_model=list[CourseOutput])
async def course_list(db: AsyncSession = Depends(get_db)):
    result = await db.scalars(select(Course).where(Course.is_active == True).order_by(Course.id))
    return list(result.all())


@router.get("/{course_id}/", response_model=CourseOutput)
async def course_detail(course_id: int, db: AsyncSession = Depends(get_db)):
    course = await db.get(Course, course_id)
    if course is None or not course.is_active:
        raise HTTPException(status_code=404, detail="Course not found")
    return course


@router.post("/", response_model=CourseOutput, status_code=201)
async def course_create(
    data: CourseCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_teacher),
):
    if await db.get(Category, data.category_id) is None:
        raise HTTPException(status_code=404, detail="Category not found")
    course = Course(**data.model_dump(), teacher_id=current_user.id)
    db.add(course)
    await db.commit()
    await db.refresh(course)
    return course


@router.put("/{course_id}/", response_model=CourseOutput)
async def course_update(
    course_id: int,
    data: CourseCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_teacher),
):
    course = await db.get(Course, course_id)
    if course is None:
        raise HTTPException(status_code=404, detail="Course not found")
    check_course_owner(course, current_user)
    if await db.get(Category, data.category_id) is None:
        raise HTTPException(status_code=404, detail="Category not found")
    for field, value in data.model_dump().items():
        setattr(course, field, value)
    await db.commit()
    await db.refresh(course)
    return course


@router.delete("/{course_id}/", status_code=204)
async def course_delete(
    course_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_teacher),
):
    course = await db.get(Course, course_id)
    if course is None:
        raise HTTPException(status_code=404, detail="Course not found")
    check_course_owner(course, current_user)
    if await db.scalar(select(StudyGroup.id).where(StudyGroup.course_id == course_id).limit(1)):
        raise HTTPException(status_code=409, detail="У курса есть группы")
    if await db.scalar(select(Application.id).where(Application.course_id == course_id).limit(1)):
        raise HTTPException(status_code=409, detail="У курса есть заявки")
    await db.delete(course)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail="Курс используется в других записях")
    return Response(status_code=204)
