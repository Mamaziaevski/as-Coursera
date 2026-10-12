from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from mysite.database.db import get_db
from mysite.database.model import Application, Course, User
from mysite.database.schema import ApplicationCreate, ApplicationUpdate, ApplicationOutput
from mysite.permissions import get_student, get_manager, check_course_access

router = APIRouter(prefix='/applications', tags=["applications"])


@router.post("/", response_model=ApplicationOutput, status_code=201)
async def application_create(
    data: ApplicationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_student),
):
    course = await db.get(Course, data.course_id)
    if course is None:
        raise HTTPException(status_code=404, detail="Course not found")
    check_course_access(course, current_user)
    application = Application(**data.model_dump(), student_id=current_user.id)
    db.add(application)
    await db.commit()
    await db.refresh(application)
    return application

@router.get("/{application_id}/", response_model=ApplicationOutput)
async def application_detail(
    application_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_manager),
):
    application = await db.get(Application, application_id)
    if application is None:
        raise HTTPException(status_code=404, detail="Application not found")
    return application


@router.get("/", response_model=list[ApplicationOutput])
async def application_list(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_manager),
):
    result = await db.scalars(select(Application).order_by(Application.id))
    return list(result.all())

@router.patch("/{application_id}/", response_model=ApplicationOutput)
async def application_update(
    application_id: int,
    data: ApplicationUpdate,
    db: AsyncSession = Depends(get_db),
   current_user: User = Depends(get_manager),
):
    application = await application_detail(application_id, db, current_user)
    application.status = data.status
    if data.comment is not None:
        application.comment = data.comment
    application.manager_id = current_user.id
    await db.commit()
    await db.refresh(application)
    return application


@router.delete("/{application_id}/", status_code=204)
async def application_delete(
    application_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_manager),
):
    application = await application_detail(application_id, db, current_user)
    await db.delete(application)
    await db.commit()
    return Response(status_code=204)