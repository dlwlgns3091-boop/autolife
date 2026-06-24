from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import WeeklyItem
from ..schemas import WeeklyItemCreate, WeeklyItemUpdate, WeeklyItemOut

router = APIRouter(prefix="/weekly", tags=["weekly"])


@router.get("", response_model=list[WeeklyItemOut])
def list_items(db: Session = Depends(get_db)):
    return db.query(WeeklyItem).order_by(WeeklyItem.sort_order, WeeklyItem.id).all()


@router.post("", response_model=WeeklyItemOut, status_code=status.HTTP_201_CREATED)
def create_item(body: WeeklyItemCreate, db: Session = Depends(get_db)):
    max_order = db.query(WeeklyItem).count()
    item = WeeklyItem(**body.model_dump(), sort_order=max_order)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.put("/{item_id}", response_model=WeeklyItemOut)
def update_item(item_id: int, body: WeeklyItemUpdate, db: Session = Depends(get_db)):
    item = db.get(WeeklyItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: int, db: Session = Depends(get_db)):
    item = db.get(WeeklyItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(item)
    db.commit()


@router.patch("/{item_id}/check", response_model=WeeklyItemOut)
def toggle_check(item_id: int, db: Session = Depends(get_db)):
    item = db.get(WeeklyItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    item.checked = not item.checked
    db.commit()
    db.refresh(item)
    return item


@router.post("/reset", status_code=status.HTTP_204_NO_CONTENT)
def reset_checks(db: Session = Depends(get_db)):
    db.query(WeeklyItem).update({"checked": False})
    db.commit()
