from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import asc, nullslast
from ..database import get_db
from ..models import ImmediateTask
from ..schemas import (
    ImmediateTaskCreate, ImmediateTaskUpdate, ImmediateTaskOut,
    BulkImportRequest, BulkPreviewLine, BulkPreviewResponse,
)

router = APIRouter(prefix="/immediate", tags=["immediate"])


def _sorted_q(q):
    return q.order_by(ImmediateTask.priority.desc(), nullslast(asc(ImmediateTask.deadline)))


@router.get("", response_model=list[ImmediateTaskOut])
def list_tasks(status: Optional[str] = Query(None), db: Session = Depends(get_db)):
    q = db.query(ImmediateTask)
    if status == "done":
        q = q.filter(ImmediateTask.status == "done")
    else:
        q = q.filter(ImmediateTask.status != "done")
    return _sorted_q(q).all()


@router.post("", response_model=ImmediateTaskOut, status_code=201)
def create_task(data: ImmediateTaskCreate, db: Session = Depends(get_db)):
    task = ImmediateTask(**data.model_dump())
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.get("/{task_id}", response_model=ImmediateTaskOut)
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = db.get(ImmediateTask, task_id)
    if not task:
        raise HTTPException(404, "Not found")
    return task


@router.put("/{task_id}", response_model=ImmediateTaskOut)
def update_task(task_id: int, data: ImmediateTaskUpdate, db: Session = Depends(get_db)):
    task = db.get(ImmediateTask, task_id)
    if not task:
        raise HTTPException(404, "Not found")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(task, k, v)
    db.commit()
    db.refresh(task)
    return task


@router.patch("/{task_id}/status", response_model=ImmediateTaskOut)
def update_status(task_id: int, status: str = Query(...), db: Session = Depends(get_db)):
    if status not in ("pending", "in_progress", "done"):
        raise HTTPException(400, "Invalid status")
    task = db.get(ImmediateTask, task_id)
    if not task:
        raise HTTPException(404, "Not found")
    task.status = status
    db.commit()
    db.refresh(task)
    return task


@router.delete("/{task_id}", status_code=204)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.get(ImmediateTask, task_id)
    if not task:
        raise HTTPException(404, "Not found")
    db.delete(task)
    db.commit()


@router.post("/bulk/preview", response_model=BulkPreviewResponse)
def bulk_preview(data: BulkImportRequest):
    lines = _parse_bulk(data.text)
    return BulkPreviewResponse(preview=lines, count=len(lines))


@router.post("/bulk", response_model=list[ImmediateTaskOut], status_code=201)
def bulk_create(data: BulkImportRequest, db: Session = Depends(get_db)):
    lines = _parse_bulk(data.text)
    created = []
    for line in lines:
        task = ImmediateTask(
            title=line.title,
            priority=line.priority,
            deadline=line.deadline,
            memo=line.memo,
            status="pending",
        )
        db.add(task)
        db.flush()
        created.append(task)
    db.commit()
    for t in created:
        db.refresh(t)
    return created


def _parse_bulk(text: str) -> list[BulkPreviewLine]:
    result = []
    for raw in text.strip().splitlines():
        raw = raw.strip()
        if not raw:
            continue
        parts = [p.strip() for p in raw.split("|")]
        title = parts[0] if parts else ""
        if not title:
            continue
        priority = 3
        if len(parts) > 1 and parts[1]:
            try:
                priority = max(1, min(5, int(parts[1])))
            except ValueError:
                pass
        deadline = None
        if len(parts) > 2 and parts[2]:
            try:
                deadline = date.fromisoformat(parts[2])
            except ValueError:
                pass
        memo = parts[3] if len(parts) > 3 and parts[3] else None
        result.append(BulkPreviewLine(title=title, priority=priority, deadline=deadline, memo=memo))
    return result
