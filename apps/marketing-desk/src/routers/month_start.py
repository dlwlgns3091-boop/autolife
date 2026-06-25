from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import MonthStartTask, MonthStartHospitalCafe, MonthStartHospitalReview
from ..schemas import ChecklistItemCreate, ChecklistItemUpdate, ChecklistItemOut, HospitalOut

router = APIRouter(prefix="/month-start", tags=["month-start"])


# ── Tasks ───────────────────────────────────────────────────────────────────

@router.get("/tasks", response_model=List[ChecklistItemOut])
def list_tasks(db: Session = Depends(get_db)):
    return db.query(MonthStartTask).order_by(MonthStartTask.order, MonthStartTask.id).all()


@router.post("/tasks", response_model=ChecklistItemOut, status_code=201)
def create_task(data: ChecklistItemCreate, db: Session = Depends(get_db)):
    item = MonthStartTask(**data.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.put("/tasks/{item_id}", response_model=ChecklistItemOut)
def update_task(item_id: int, data: ChecklistItemUpdate, db: Session = Depends(get_db)):
    item = db.get(MonthStartTask, item_id)
    if not item:
        raise HTTPException(404, "Not found")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(item, k, v)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/tasks/{item_id}", status_code=204)
def delete_task(item_id: int, db: Session = Depends(get_db)):
    item = db.get(MonthStartTask, item_id)
    if not item:
        raise HTTPException(404, "Not found")
    db.delete(item)
    db.commit()


@router.patch("/tasks/{item_id}/check", response_model=ChecklistItemOut)
def check_task(item_id: int, checked: bool = Query(...), db: Session = Depends(get_db)):
    item = db.get(MonthStartTask, item_id)
    if not item:
        raise HTTPException(404, "Not found")
    item.is_checked = checked
    db.commit()
    db.refresh(item)
    return item


# ── Cafe hospitals ──────────────────────────────────────────────────────────

@router.get("/hospitals/cafe", response_model=List[HospitalOut])
def list_cafe(db: Session = Depends(get_db)):
    return db.query(MonthStartHospitalCafe).order_by(
        MonthStartHospitalCafe.order, MonthStartHospitalCafe.id
    ).all()


@router.patch("/hospitals/cafe/{item_id}/check", response_model=HospitalOut)
def check_cafe(item_id: int, checked: bool = Query(...), db: Session = Depends(get_db)):
    item = db.get(MonthStartHospitalCafe, item_id)
    if not item:
        raise HTTPException(404, "Not found")
    item.is_checked = checked
    db.commit()
    db.refresh(item)
    return item


# ── Review hospitals ────────────────────────────────────────────────────────

@router.get("/hospitals/review", response_model=List[HospitalOut])
def list_review(db: Session = Depends(get_db)):
    return db.query(MonthStartHospitalReview).order_by(
        MonthStartHospitalReview.order, MonthStartHospitalReview.id
    ).all()


@router.patch("/hospitals/review/{item_id}/check", response_model=HospitalOut)
def check_review(item_id: int, checked: bool = Query(...), db: Session = Depends(get_db)):
    item = db.get(MonthStartHospitalReview, item_id)
    if not item:
        raise HTTPException(404, "Not found")
    item.is_checked = checked
    db.commit()
    db.refresh(item)
    return item


# ── Reset ───────────────────────────────────────────────────────────────────

@router.post("/reset", status_code=204)
def reset_month_start(db: Session = Depends(get_db)):
    db.query(MonthStartTask).update({"is_checked": False})
    db.query(MonthStartHospitalCafe).update({"is_checked": False})
    db.query(MonthStartHospitalReview).update({"is_checked": False})
    db.commit()
