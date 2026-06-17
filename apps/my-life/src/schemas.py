from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel


# ── Todo ──────────────────────────────────────────────────────────────────────
class TodoCreate(BaseModel):
    title: str
    priority: int = 3
    status: str = "pending"
    due_date: Optional[date] = None
    memo: Optional[str] = None


class TodoUpdate(BaseModel):
    title: Optional[str] = None
    priority: Optional[int] = None
    status: Optional[str] = None
    due_date: Optional[date] = None
    memo: Optional[str] = None


class TodoOut(BaseModel):
    id: int
    title: str
    priority: int
    status: str
    due_date: Optional[date]
    memo: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ── Budget Category ───────────────────────────────────────────────────────────
class CategoryCreate(BaseModel):
    name: str


class CategoryOut(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}


# ── Budget Entry ──────────────────────────────────────────────────────────────
class BudgetEntryCreate(BaseModel):
    date: date
    amount: int
    category_id: Optional[int] = None
    entry_type: str  # income / expense
    memo: Optional[str] = None


class BudgetEntryUpdate(BaseModel):
    date: Optional[date] = None
    amount: Optional[int] = None
    category_id: Optional[int] = None
    entry_type: Optional[str] = None
    memo: Optional[str] = None


class BudgetEntryOut(BaseModel):
    id: int
    date: date
    amount: int
    category_id: Optional[int]
    entry_type: str
    memo: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class MonthlySummary(BaseModel):
    year: int
    month: int
    total_income: int
    total_expense: int
    balance: int
    by_category: list[dict]
