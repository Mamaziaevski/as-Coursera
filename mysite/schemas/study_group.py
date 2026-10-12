from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from mysite.database.db import get_db, begin_group_write
from mysite.database.model import Course, StudyGroup, Enrollment, EnrollmentStatus, User
from mysite.database.schema import StudyGroupCreate, StudyGroupOutput
from mysite.permissions import get_teacher, check_course_owner

router = APIRouter(prefix="/groups", tags=["Study Groups"])


@router.get("/", response_model=list[StudyGroupOutput])
async def studygroup_list(db: AsyncSession = Depends(get_db)):
    result = await db.scalars(select(StudyGroup).order_by(StudyGroup.id))
    return list(result.all())


@router.get("/{group_id}/", response_model=StudyGroupOutput)
async def studygroup_detail(group_id: int, db: AsyncSession = Depends(get_db)):
    group = await db.get(StudyGroup, group_id)
    if group is None:
        raise HTTPException(status_code=404, detail="Group not found")
    return group


@router.post("/", response_model=StudyGroupOutput, status_code=201)
async def studygroup_create(
    data: StudyGroupCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_teacher),
):
    course = await db.get(Course, data.course_id)
    if course is None:
        raise HTTPException(status_code=404, detail="Course not found")
    check_course_owner(course, current_user)
    group = StudyGroup(**data.model_dump(), teacher_id=current_user.id)
    db.add(group)
    await db.commit()
    await db.refresh(group)
    return group


@router.put("/{group_id}/", response_model=StudyGroupOutput)
async def studygroup_update(
    group_id: int,
    data: StudyGroupCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_teacher),
):
    user_id = current_user.id
    await begin_group_write(db)
    group = await studygroup_detail(group_id, db)
    if group.teacher_id != user_id:
        raise HTTPException(status_code=403, detail="Можно изменять только свою группу")
    if data.course_id != group.course_id:
        raise HTTPException(status_code=409, detail="Нельзя переносить группу на другой курс")
    count = await db.scalar(select(func.count(Enrollment.id)).where(
        Enrollment.group_id == group.id, Enrollment.status != EnrollmentStatus.cancelled,
    ))
    if data.capacity < count:
        raise HTTPException(status_code=409, detail="Вместимость меньше числа участников")
    for field, value in data.model_dump().items():
        setattr(group, field, value)
    await db.commit()
    await db.refresh(group)
    return group


@router.delete("/{group_id}/", status_code=204)
async def studygroup_delete(
    group_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_teacher),
):
    group = await studygroup_detail(group_id, db)
    if group.teacher_id != current_user.id:
        raise HTTPException(status_code=403, detail="Можно удалять только свою группу")
    if await db.scalar(select(Enrollment.id).where(Enrollment.group_id == group_id).limit(1)):
        raise HTTPException(status_code=409, detail="У группы есть зачисления")
    await db.delete(group)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail="У группы появились зачисления")
    return Response(status_code=204)
