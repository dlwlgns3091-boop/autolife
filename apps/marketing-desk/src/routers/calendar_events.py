from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from ..models import CalendarEvent
from ..schemas import CalendarEventCreate, CalendarEventUpdate, CalendarEventOut

router = APIRouter(prefix="/calendar", tags=["calendar"])


@router.get("", response_model=List[CalendarEventOut])
def list_events(year: Optional[int] = None, month: Optional[int] = None, db: Session = Depends(get_db)):
    q = db.query(CalendarEvent)
    if year and month:
        from datetime import date
        start = date(year, month, 1)
        if month == 12:
            end = date(year + 1, 1, 1)
        else:
            end = date(year, month + 1, 1)
        q = q.filter(CalendarEvent.event_date >= start, CalendarEvent.event_date < end)
    return q.order_by(CalendarEvent.event_date, CalendarEvent.id).all()


@router.post("", response_model=CalendarEventOut, status_code=201)
def create_event(data: CalendarEventCreate, db: Session = Depends(get_db)):
    item = CalendarEvent(**data.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.get("/{event_id}", response_model=CalendarEventOut)
def get_event(event_id: int, db: Session = Depends(get_db)):
    item = db.get(CalendarEvent, event_id)
    if not item:
        raise HTTPException(404, "Not found")
    return item


@router.put("/{event_id}", response_model=CalendarEventOut)
def update_event(event_id: int, data: CalendarEventUpdate, db: Session = Depends(get_db)):
    item = db.get(CalendarEvent, event_id)
    if not item:
        raise HTTPException(404, "Not found")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(item, k, v)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{event_id}", status_code=204)
def delete_event(event_id: int, db: Session = Depends(get_db)):
    item = db.get(CalendarEvent, event_id)
    if not item:
        raise HTTPException(404, "Not found")
    db.delete(item)
    db.commit()
