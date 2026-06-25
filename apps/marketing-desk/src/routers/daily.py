from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import DailyTask
from ..schemas import ChecklistItemCreate, ChecklistItemUpdate, ChecklistItemOut

router = APIRouter(prefix="/daily", tags=["daily"])


@router.get("", response_model=List[ChecklistItemOut])
def list_items(db: Session = Depends(get_db)):
    return db.query(DailyTask).order_by(DailyTask.order, DailyTask.id).all()


@router.post("", response_model=ChecklistItemOut, status_code=201)
def create_item(data: ChecklistItemCreate, db: Session = Depends(get_db)):
    item = DailyTask(**data.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.put("/{item_id}", response_model=ChecklistItemOut)
def update_item(item_id: int, data: ChecklistItemUpdate, db: Session = Depends(get_db)):
    item = db.get(DailyTask, item_id)
    if not item:
        raise HTTPException(404, "Not found")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(item, k, v)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{item_id}", status_code=204)
def delete_item(item_id: int, db: Session = Depends(get_db)):
    item = db.get(DailyTask, item_id)
    if not item:
        raise HTTPException(404, "Not found")
    db.delete(item)
    db.commit()


@router.patch("/{item_id}/check", response_model=ChecklistItemOut)
def toggle_check(item_id: int, checked: bool = Query(...), db: Session = Depends(get_db)):
    item = db.get(DailyTask, item_id)
    if not item:
        raise HTTPException(404, "Not found")
    item.is_checked = checked
    db.commit()
    db.refresh(item)
    return item


@router.post("/reset", status_code=204)
def reset_daily(db: Session = Depends(get_db)):
    db.query(DailyTask).update({"is_checked": False})
    db.commit()
