from datetime import date
from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import BudgetEntry, BudgetCategory
from ..schemas import (
    BudgetEntryCreate, BudgetEntryUpdate, BudgetEntryOut,
    CategoryCreate, CategoryOut, MonthlySummary,
)
from ..auth import require_auth

router = APIRouter(prefix="/api/budget", tags=["budget"])


# ── Categories ────────────────────────────────────────────────────────────────
@router.get("/categories", response_model=list[CategoryOut])
def list_categories(request: Request, db: Session = Depends(get_db)):
    require_auth(request)
    return db.query(BudgetCategory).order_by(BudgetCategory.name).all()


@router.post("/categories", response_model=CategoryOut, status_code=201)
def create_category(request: Request, body: CategoryCreate, db: Session = Depends(get_db)):
    require_auth(request)
    cat = BudgetCategory(name=body.name)
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat


@router.delete("/categories/{cat_id}", status_code=204)
def delete_category(request: Request, cat_id: int, db: Session = Depends(get_db)):
    require_auth(request)
    cat = db.get(BudgetCategory, cat_id)
    if not cat:
        raise HTTPException(404, "Not found")
    db.delete(cat)
    db.commit()


# ── Entries ───────────────────────────────────────────────────────────────────
@router.get("/entries", response_model=list[BudgetEntryOut])
def list_entries(
    request: Request,
    year: int = 0,
    month: int = 0,
    db: Session = Depends(get_db),
):
    require_auth(request)
    today = date.today()
    y = year or today.year
    m = month or today.month
    q = (
        db.query(BudgetEntry)
        .filter(
            func.strftime("%Y", BudgetEntry.date) == str(y),
            func.strftime("%m", BudgetEntry.date) == f"{m:02d}",
        )
        .order_by(BudgetEntry.date.desc(), BudgetEntry.created_at.desc())
    )
    return q.all()


@router.post("/entries", response_model=BudgetEntryOut, status_code=201)
def create_entry(request: Request, body: BudgetEntryCreate, db: Session = Depends(get_db)):
    require_auth(request)
    entry = BudgetEntry(**body.model_dump())
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


@router.put("/entries/{entry_id}", response_model=BudgetEntryOut)
def update_entry(request: Request, entry_id: int, body: BudgetEntryUpdate, db: Session = Depends(get_db)):
    require_auth(request)
    entry = db.get(BudgetEntry, entry_id)
    if not entry:
        raise HTTPException(404, "Not found")
    for k, v in body.model_dump(exclude_none=True).items():
        setattr(entry, k, v)
    db.commit()
    db.refresh(entry)
    return entry


@router.delete("/entries/{entry_id}", status_code=204)
def delete_entry(request: Request, entry_id: int, db: Session = Depends(get_db)):
    require_auth(request)
    entry = db.get(BudgetEntry, entry_id)
    if not entry:
        raise HTTPException(404, "Not found")
    db.delete(entry)
    db.commit()


# ── Monthly Summary ───────────────────────────────────────────────────────────
@router.get("/summary", response_model=MonthlySummary)
def monthly_summary(
    request: Request,
    year: int = 0,
    month: int = 0,
    db: Session = Depends(get_db),
):
    require_auth(request)
    today = date.today()
    y = year or today.year
    m = month or today.month

    entries = (
        db.query(BudgetEntry)
        .filter(
            func.strftime("%Y", BudgetEntry.date) == str(y),
            func.strftime("%m", BudgetEntry.date) == f"{m:02d}",
        )
        .all()
    )

    total_income = sum(e.amount for e in entries if e.entry_type == "income")
    total_expense = sum(e.amount for e in entries if e.entry_type == "expense")

    cat_map: dict[int | None, int] = {}
    for e in entries:
        if e.entry_type == "expense":
            cat_map[e.category_id] = cat_map.get(e.category_id, 0) + e.amount

    cats = {c.id: c.name for c in db.query(BudgetCategory).all()}
    by_category = [
        {"category_id": cid, "name": cats.get(cid, "미분류"), "amount": amt}
        for cid, amt in sorted(cat_map.items(), key=lambda x: -x[1])
    ]

    return MonthlySummary(
        year=y, month=m,
        total_income=total_income,
        total_expense=total_expense,
        balance=total_income - total_expense,
        by_category=by_category,
    )
