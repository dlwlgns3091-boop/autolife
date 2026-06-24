from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import MonthlyItem
from ..schemas import MonthlyItemCreate, MonthlyItemUpdate, MonthlyItemOut

router = APIRouter(prefix="/monthly", tags=["monthly"])


@router.get("", response_model=list[MonthlyItemOut])
def list_items(db: Session = Depends(get_db)):
    period_order = {"월초": 0, "월중": 1, "월말": 2}
    items = db.query(MonthlyItem).order_by(MonthlyItem.sort_order, MonthlyItem.id).all()
    return sorted(items, key=lambda x: (period_order.get(x.period, 99), x.sort_order, x.id))


@router.post("", response_model=MonthlyItemOut, status_code=status.HTTP_201_CREATED)
def create_item(body: MonthlyItemCreate, db: Session = Depends(get_db)):
    max_order = db.query(MonthlyItem).filter(MonthlyItem.period == body.period).count()
    item = MonthlyItem(**body.model_dump(), sort_order=max_order)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.put("/{item_id}", response_model=MonthlyItemOut)
def update_item(item_id: int, body: MonthlyItemUpdate, db: Session = Depends(get_db)):
    item = db.get(MonthlyItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: int, db: Session = Depends(get_db)):
    item = db.get(MonthlyItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(item)
    db.commit()


@router.patch("/{item_id}/check", response_model=MonthlyItemOut)
def toggle_check(item_id: int, db: Session = Depends(get_db)):
    item = db.get(MonthlyItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    item.checked = not item.checked
    db.commit()
    db.refresh(item)
    return item


@router.post("/reset", status_code=status.HTTP_204_NO_CONTENT)
def reset_checks(db: Session = Depends(get_db)):
    db.query(MonthlyItem).update({"checked": False})
    db.commit()
