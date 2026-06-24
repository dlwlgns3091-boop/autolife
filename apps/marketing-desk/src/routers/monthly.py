from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import MonthlyRoutine
from ..schemas import MonthlyRoutineCreate, MonthlyRoutineUpdate, MonthlyRoutineOut

router = APIRouter(prefix="/monthly", tags=["monthly"])
VALID_GROUPS = {"early", "mid", "late"}


@router.get("", response_model=list[MonthlyRoutineOut])
def list_items(db: Session = Depends(get_db)):
    group_order = {"early": 0, "mid": 1, "late": 2}
    items = db.query(MonthlyRoutine).order_by(MonthlyRoutine.order, MonthlyRoutine.id).all()
    return sorted(items, key=lambda x: (group_order.get(x.group, 3), x.order, x.id))


@router.post("", response_model=MonthlyRoutineOut, status_code=201)
def create_item(data: MonthlyRoutineCreate, db: Session = Depends(get_db)):
    if data.group not in VALID_GROUPS:
        raise HTTPException(400, "group must be early, mid, or late")
    item = MonthlyRoutine(**data.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.get("/{item_id}", response_model=MonthlyRoutineOut)
def get_item(item_id: int, db: Session = Depends(get_db)):
    item = db.get(MonthlyRoutine, item_id)
    if not item:
        raise HTTPException(404, "Not found")
    return item


@router.put("/{item_id}", response_model=MonthlyRoutineOut)
def update_item(item_id: int, data: MonthlyRoutineUpdate, db: Session = Depends(get_db)):
    item = db.get(MonthlyRoutine, item_id)
    if not item:
        raise HTTPException(404, "Not found")
    payload = data.model_dump(exclude_unset=True)
    if "group" in payload and payload["group"] not in VALID_GROUPS:
        raise HTTPException(400, "group must be early, mid, or late")
    for k, v in payload.items():
        setattr(item, k, v)
    db.commit()
    db.refresh(item)
    return item


@router.patch("/{item_id}/check", response_model=MonthlyRoutineOut)
def toggle_check(item_id: int, checked: bool = Query(...), db: Session = Depends(get_db)):
    item = db.get(MonthlyRoutine, item_id)
    if not item:
        raise HTTPException(404, "Not found")
    item.is_checked = checked
    db.commit()
    db.refresh(item)
    return item


@router.post("/reset", status_code=204)
def reset_month(db: Session = Depends(get_db)):
    db.query(MonthlyRoutine).update({"is_checked": False})
    db.commit()


@router.delete("/{item_id}", status_code=204)
def delete_item(item_id: int, db: Session = Depends(get_db)):
    item = db.get(MonthlyRoutine, item_id)
    if not item:
        raise HTTPException(404, "Not found")
    db.delete(item)
    db.commit()
