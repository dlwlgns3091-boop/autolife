from datetime import date as date_type
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from ..models import AlwaysTask
from ..schemas import (
    AlwaysTaskCreate, AlwaysTaskUpdate, AlwaysTaskOut,
    BulkImportRequest, BulkPreviewLine, BulkPreviewResponse,
)

router = APIRouter(prefix="/always", tags=["always"])

VALID_STATUSES = {"pending", "in_progress", "done"}


def _parse_bulk_lines(text: str) -> List[BulkPreviewLine]:
    results = []
    for raw in text.strip().splitlines():
        raw = raw.strip()
        if not raw:
            continue
        parts = [p.strip() for p in raw.split("|")]
        title = parts[0] if len(parts) > 0 else ""
        if not title:
            continue
        try:
            priority = max(1, min(5, int(parts[1]))) if len(parts) > 1 and parts[1] else 3
        except ValueError:
            priority = 3
        deadline = None
        if len(parts) > 2 and parts[2]:
            try:
                deadline = date_type.fromisoformat(parts[2])
            except ValueError:
                pass
        memo = parts[3] if len(parts) > 3 and parts[3] else None
        results.append(BulkPreviewLine(title=title, priority=priority, deadline=deadline, memo=memo))
    return results


@router.get("", response_model=List[AlwaysTaskOut])
def list_tasks(status: Optional[str] = None, db: Session = Depends(get_db)):
    q = db.query(AlwaysTask)
    if status:
        q = q.filter(AlwaysTask.status == status)
    else:
        q = q.filter(AlwaysTask.status != "done")
    return q.order_by(AlwaysTask.priority.desc(), AlwaysTask.id).all()


@router.post("", response_model=AlwaysTaskOut, status_code=201)
def create_task(data: AlwaysTaskCreate, db: Session = Depends(get_db)):
    item = AlwaysTask(**data.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.get("/{item_id}", response_model=AlwaysTaskOut)
def get_task(item_id: int, db: Session = Depends(get_db)):
    item = db.get(AlwaysTask, item_id)
    if not item:
        raise HTTPException(404, "Not found")
    return item


@router.put("/{item_id}", response_model=AlwaysTaskOut)
def update_task(item_id: int, data: AlwaysTaskUpdate, db: Session = Depends(get_db)):
    item = db.get(AlwaysTask, item_id)
    if not item:
        raise HTTPException(404, "Not found")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(item, k, v)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{item_id}", status_code=204)
def delete_task(item_id: int, db: Session = Depends(get_db)):
    item = db.get(AlwaysTask, item_id)
    if not item:
        raise HTTPException(404, "Not found")
    db.delete(item)
    db.commit()


@router.patch("/{item_id}/status", response_model=AlwaysTaskOut)
def set_status(item_id: int, status: str = Query(...), db: Session = Depends(get_db)):
    if status not in VALID_STATUSES:
        raise HTTPException(400, f"status must be one of {VALID_STATUSES}")
    item = db.get(AlwaysTask, item_id)
    if not item:
        raise HTTPException(404, "Not found")
    item.status = status
    db.commit()
    db.refresh(item)
    return item


@router.post("/bulk/preview", response_model=BulkPreviewResponse)
def bulk_preview(data: BulkImportRequest):
    lines = _parse_bulk_lines(data.text)
    return BulkPreviewResponse(preview=lines, count=len(lines))


@router.post("/bulk", response_model=List[AlwaysTaskOut], status_code=201)
def bulk_create(data: BulkImportRequest, db: Session = Depends(get_db)):
    lines = _parse_bulk_lines(data.text)
    items = []
    for ln in lines:
        item = AlwaysTask(
            title=ln.title,
            priority=ln.priority,
            deadline=ln.deadline,
            memo=ln.memo,
        )
        db.add(item)
        items.append(item)
    db.commit()
    for item in items:
        db.refresh(item)
    return items
