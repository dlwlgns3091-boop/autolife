from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import WeeklyRoutine
from ..schemas import WeeklyRoutineCreate, WeeklyRoutineUpdate, WeeklyRoutineOut

router = APIRouter(prefix="/weekly", tags=["weekly"])


@router.get("", response_model=list[WeeklyRoutineOut])
def list_items(db: Session = Depends(get_db)):
    return db.query(WeeklyRoutine).order_by(WeeklyRoutine.order, WeeklyRoutine.id).all()


@router.post("", response_model=WeeklyRoutineOut, status_code=201)
def create_item(data: WeeklyRoutineCreate, db: Session = Depends(get_db)):
    item = WeeklyRoutine(**data.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.get("/{item_id}", response_model=WeeklyRoutineOut)
def get_item(item_id: int, db: Session = Depends(get_db)):
    item = db.get(WeeklyRoutine, item_id)
    if not item:
        raise HTTPException(404, "Not found")
    return item


@router.put("/{item_id}", response_model=WeeklyRoutineOut)
def update_item(item_id: int, data: WeeklyRoutineUpdate, db: Session = Depends(get_db)):
    item = db.get(WeeklyRoutine, item_id)
    if not item:
        raise HTTPException(404, "Not found")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(item, k, v)
    db.commit()
    db.refresh(item)
    return item


@router.patch("/{item_id}/check", response_model=WeeklyRoutineOut)
def toggle_check(item_id: int, checked: bool = Query(...), db: Session = Depends(get_db)):
    item = db.get(WeeklyRoutine, item_id)
    if not item:
        raise HTTPException(404, "Not found")
    item.is_checked = checked
    db.commit()
    db.refresh(item)
    return item


@router.post("/reset", status_code=204)
def reset_week(db: Session = Depends(get_db)):
    db.query(WeeklyRoutine).update({"is_checked": False})
    db.commit()


@router.delete("/{item_id}", status_code=204)
def delete_item(item_id: int, db: Session = Depends(get_db)):
    item = db.get(WeeklyRoutine, item_id)
    if not item:
        raise HTTPException(404, "Not found")
    db.delete(item)
    db.commit()
