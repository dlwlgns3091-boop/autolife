from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import asc, desc
from typing import List, Optional

from ..database import get_db
from ..models import Task
from ..schemas import TaskCreate, TaskUpdate, TaskOut, SummaryOut

router = APIRouter(prefix="/tasks", tags=["tasks"])


def _base_query(db: Session):
    return db.query(Task)


@router.get("/summary", response_model=SummaryOut)
def get_summary(db: Session = Depends(get_db)):
    today = date.today()
    today_count = db.query(Task).filter(
        Task.due_date == today,
        Task.status != "완료"
    ).count()
    overdue_count = db.query(Task).filter(
        Task.due_date < today,
        Task.status != "완료"
    ).count()
    in_progress_count = db.query(Task).filter(Task.status == "진행중").count()
    return SummaryOut(
        today_count=today_count,
        overdue_count=overdue_count,
        in_progress_count=in_progress_count,
    )


@router.get("", response_model=List[TaskOut])
def list_tasks(
    status: Optional[str] = Query(None, description="대기 / 진행중 / 완료 / incomplete"),
    category_id: Optional[int] = Query(None),
    clinic: Optional[str] = Query(None),
    period: Optional[str] = Query(None, description="today / week"),
    db: Session = Depends(get_db),
):
    q = db.query(Task)
    today = date.today()

    if status == "incomplete":
        q = q.filter(Task.status != "완료")
    elif status:
        q = q.filter(Task.status == status)

    if category_id is not None:
        q = q.filter(Task.category_id == category_id)

    if clinic:
        q = q.filter(Task.clinic.ilike(f"%{clinic}%"))

    if period == "today":
        q = q.filter(Task.due_date == today)
    elif period == "week":
        from datetime import timedelta
        week_end = today + timedelta(days=6)
        q = q.filter(Task.due_date >= today, Task.due_date <= week_end)

    # 우선순위 높은 순(desc) → 마감 임박 순(asc, null last)
    q = q.order_by(
        desc(Task.priority),
        asc(Task.due_date.is_(None)),
        asc(Task.due_date),
    )
    return q.all()


@router.post("", response_model=TaskOut, status_code=201)
def create_task(body: TaskCreate, db: Session = Depends(get_db)):
    task = Task(**body.model_dump())
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.get("/{task_id}", response_model=TaskOut)
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="업무를 찾을 수 없습니다.")
    return task


@router.patch("/{task_id}", response_model=TaskOut)
def update_task(task_id: int, body: TaskUpdate, db: Session = Depends(get_db)):
    task = db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="업무를 찾을 수 없습니다.")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(task, field, value)
    db.commit()
    db.refresh(task)
    return task


@router.delete("/{task_id}", status_code=204)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="업무를 찾을 수 없습니다.")
    db.delete(task)
    db.commit()
