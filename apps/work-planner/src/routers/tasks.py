from datetime import date, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import case, asc, nullslast
from ..database import get_db
from ..models import Task, TaskCategory
from ..schemas import TaskCreate, TaskUpdate, TaskOut, BulkCreateRequest, BulkPreviewResponse, BulkTaskLine, SummaryOut

router = APIRouter(prefix="/tasks", tags=["tasks"])


def _task_out(t: Task) -> TaskOut:
    return TaskOut(
        id=t.id,
        title=t.title,
        category_id=t.category_id,
        category_name=t.category.name if t.category else None,
        priority=t.priority,
        status=t.status,
        deadline=t.deadline,
        recurrence=t.recurrence,
        memo=t.memo,
        source=t.source or "직접",
    )


def _sorted_incomplete(query):
    """Sort: priority DESC (1 is lowest, 5 is highest), deadline ASC (nulls last)."""
    return query.order_by(
        Task.priority.desc(),
        nullslast(asc(Task.deadline)),
    )


@router.get("/summary", response_model=SummaryOut)
def get_summary(db: Session = Depends(get_db)):
    today = date.today()
    week_end = today + timedelta(days=7 - today.weekday())

    today_count = db.query(Task).filter(
        Task.status != "done",
        Task.deadline == today,
    ).count()

    overdue_count = db.query(Task).filter(
        Task.status != "done",
        Task.deadline < today,
        Task.deadline.isnot(None),
    ).count()

    in_progress_count = db.query(Task).filter(Task.status == "in_progress").count()

    return SummaryOut(
        today_count=today_count,
        overdue_count=overdue_count,
        in_progress_count=in_progress_count,
    )


@router.get("/top", response_model=Optional[TaskOut])
def get_top_task(db: Session = Depends(get_db)):
    q = db.query(Task).filter(Task.status != "done")
    q = _sorted_incomplete(q)
    t = q.first()
    return _task_out(t) if t else None


@router.get("", response_model=list[TaskOut])
def list_tasks(
    filter: Optional[str] = Query(None),  # today / week / overdue / done
    category_id: Optional[int] = Query(None),
    source: Optional[str] = Query(None),  # 반복 / 직접
    db: Session = Depends(get_db),
):
    today = date.today()
    q = db.query(Task)

    if filter == "done":
        q = q.filter(Task.status == "done")
        if source in ("반복", "직접"):
            q = q.filter(Task.source == source)
        return [_task_out(t) for t in q.order_by(Task.updated_at.desc()).all()]

    q = q.filter(Task.status != "done")

    if filter == "today":
        q = q.filter(Task.deadline == today)
    elif filter == "week":
        week_start = today
        week_end = today + timedelta(days=6 - today.weekday())
        q = q.filter(Task.deadline >= week_start, Task.deadline <= week_end)
    elif filter == "overdue":
        q = q.filter(Task.deadline < today, Task.deadline.isnot(None))

    if category_id:
        q = q.filter(Task.category_id == category_id)

    if source in ("반복", "직접"):
        q = q.filter(Task.source == source)

    q = _sorted_incomplete(q)
    return [_task_out(t) for t in q.all()]


@router.post("", response_model=TaskOut, status_code=201)
def create_task(data: TaskCreate, db: Session = Depends(get_db)):
    if data.category_id:
        if not db.get(TaskCategory, data.category_id):
            raise HTTPException(404, "Category not found")
    t = Task(**data.model_dump())
    db.add(t)
    db.commit()
    db.refresh(t)
    return _task_out(t)


@router.post("/bulk/preview", response_model=BulkPreviewResponse)
def bulk_preview(data: BulkCreateRequest):
    lines = _parse_bulk(data.text)
    return BulkPreviewResponse(preview=lines, count=len(lines))


@router.post("/bulk", response_model=list[TaskOut], status_code=201)
def bulk_create(data: BulkCreateRequest, db: Session = Depends(get_db)):
    lines = _parse_bulk(data.text)
    created = []
    for line in lines:
        cat_id = None
        if line.category_name:
            cat = db.query(TaskCategory).filter(TaskCategory.name == line.category_name).first()
            if not cat:
                cat = TaskCategory(name=line.category_name)
                db.add(cat)
                db.flush()
            cat_id = cat.id
        t = Task(
            title=line.title,
            category_id=cat_id,
            priority=line.priority,
            deadline=line.deadline,
            memo=line.memo,
            status="pending",
            source="직접",
        )
        db.add(t)
        db.flush()
        created.append(t)
    db.commit()
    for t in created:
        db.refresh(t)
    return [_task_out(t) for t in created]


def _parse_bulk(text: str) -> list[BulkTaskLine]:
    result = []
    for raw in text.strip().splitlines():
        raw = raw.strip()
        if not raw:
            continue
        parts = [p.strip() for p in raw.split("|")]
        title = parts[0] if len(parts) > 0 else ""
        if not title:
            continue
        category_name = parts[1] if len(parts) > 1 and parts[1] else None
        priority = 3
        if len(parts) > 2 and parts[2]:
            try:
                priority = max(1, min(5, int(parts[2])))
            except ValueError:
                pass
        deadline = None
        if len(parts) > 3 and parts[3]:
            try:
                from datetime import date as d
                deadline = d.fromisoformat(parts[3])
            except ValueError:
                pass
        memo = parts[4] if len(parts) > 4 and parts[4] else None
        result.append(BulkTaskLine(
            title=title,
            category_name=category_name,
            priority=priority,
            deadline=deadline,
            memo=memo,
        ))
    return result


@router.get("/{task_id}", response_model=TaskOut)
def get_task(task_id: int, db: Session = Depends(get_db)):
    t = db.get(Task, task_id)
    if not t:
        raise HTTPException(404, "Task not found")
    return _task_out(t)


@router.put("/{task_id}", response_model=TaskOut)
def update_task(task_id: int, data: TaskUpdate, db: Session = Depends(get_db)):
    t = db.get(Task, task_id)
    if not t:
        raise HTTPException(404, "Task not found")
    for field, val in data.model_dump(exclude_unset=True).items():
        setattr(t, field, val)
    db.commit()
    db.refresh(t)
    return _task_out(t)


@router.patch("/{task_id}/status", response_model=TaskOut)
def update_status(task_id: int, status: str = Query(...), db: Session = Depends(get_db)):
    if status not in ("pending", "in_progress", "done"):
        raise HTTPException(400, "Invalid status")
    t = db.get(Task, task_id)
    if not t:
        raise HTTPException(404, "Task not found")
    t.status = status
    db.commit()
    db.refresh(t)
    return _task_out(t)


@router.patch("/{task_id}/priority", response_model=TaskOut)
def update_priority(task_id: int, priority: int = Query(..., ge=1, le=5), db: Session = Depends(get_db)):
    t = db.get(Task, task_id)
    if not t:
        raise HTTPException(404, "Task not found")
    t.priority = priority
    db.commit()
    db.refresh(t)
    return _task_out(t)


@router.delete("/{task_id}", status_code=204)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    t = db.get(Task, task_id)
    if not t:
        raise HTTPException(404, "Task not found")
    db.delete(t)
    db.commit()
