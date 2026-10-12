from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from mysite.database.db import get_db, begin_group_write
from mysite.database.model import User, Course, StudyGroup, Enrollment, EnrollmentStatus, CourseStatus, Role
from mysite.database.schema import EnrollmentCreate, EnrollmentOutput
from mysite.permissions import get_student, check_course_access

router = APIRouter(prefix="/enrollments", tags=["Enrollments"])
group_router = APIRouter(prefix="/groups", tags=["Enrollments"])


@router.get("/", response_model=list[EnrollmentOutput])
async def enrollment_list(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_student),
):
    result = await db.scalars(select(Enrollment).where(
        Enrollment.student_id == current_user.id,
    ).order_by(Enrollment.id))
    return list(result.all())


@router.get("/{enrollment_id}/", response_model=EnrollmentOutput)
async def enrollment_detail(
    enrollment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_student),
):
    enrollment = await db.scalar(select(Enrollment).where(
        Enrollment.id == enrollment_id, Enrollment.student_id == current_user.id,
    ))
    if enrollment is None:
        raise HTTPException(status_code=404, detail="Enrollment not found")
    return enrollment


@group_router.post("/{group_id}/enroll/", response_model=EnrollmentOutput, status_code=201)
async def enrollment_create(
    group_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_student),
):
    user_id = current_user.id

    await begin_group_write(db)
    current_user = await db.get(User, user_id)
    if current_user is None or current_user.role != Role.student:
        raise HTTPException(status_code=403, detail="Нет доступа к записи")
    group = await db.get(StudyGroup, group_id)
    if group is None:
        raise HTTPException(status_code=404, detail="Group not found")
    if group.status != CourseStatus.recruiting:
        raise HTTPException(status_code=409, detail="Набор в группу закрыт")
    course = await db.get(Course, group.course_id)
    check_course_access(course, current_user)
    enrollment = await db.scalar(select(Enrollment).where(
        Enrollment.student_id == user_id, Enrollment.group_id == group_id,
    ))
    if enrollment is not None and enrollment.status != EnrollmentStatus.cancelled:
        raise HTTPException(status_code=409, detail="Вы уже записаны в группу")
    count = await db.scalar(select(func.count(Enrollment.id)).where(
        Enrollment.group_id == group_id, Enrollment.status != EnrollmentStatus.cancelled,
    ))
    if count >= group.capacity:
        raise HTTPException(status_code=409, detail="Свободных мест нет")
    if enrollment is None:
        enrollment = Enrollment(student_id=user_id, group_id=group_id)
        db.add(enrollment)
    else:
        enrollment.status = EnrollmentStatus.active
    await db.commit()
    await db.refresh(enrollment)
    return enrollment


@router.post("/{enrollment_id}/cancel/", response_model=EnrollmentOutput)
async def enrollment_cancel(
    enrollment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_student),
):
    enrollment = await enrollment_detail(enrollment_id, db, current_user)
    if enrollment.status == EnrollmentStatus.completed:
        raise HTTPException(status_code=409, detail="Обучение уже завершено")
    enrollment.status = EnrollmentStatus.cancelled
    await db.commit()
    await db.refresh(enrollment)
    return enrollment


@router.post("/", response_model=EnrollmentOutput, status_code=201)
async def enrollment_create_by_body(
    data: EnrollmentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_student),
):
    return await enrollment_create(data.group_id, db, current_user)
