from datetime import date
from typing import Optional, List
from pydantic import BaseModel


# ── Generic checklist item ──────────────────────────────────────────────────

class ChecklistItemCreate(BaseModel):
    title: str


class ChecklistItemUpdate(BaseModel):
    title: Optional[str] = None
    is_checked: Optional[bool] = None
    order: Optional[int] = None


class ChecklistItemOut(BaseModel):
    id: int
    title: str
    is_checked: bool
    order: int
    model_config = {"from_attributes": True}


# ── Hospital ────────────────────────────────────────────────────────────────

class HospitalOut(BaseModel):
    id: int
    name: str
    is_checked: bool
    order: int
    model_config = {"from_attributes": True}


# ── Always task ─────────────────────────────────────────────────────────────

class AlwaysTaskCreate(BaseModel):
    title: str
    priority: int = 3
    status: str = "pending"
    memo: Optional[str] = None
    deadline: Optional[date] = None


class AlwaysTaskUpdate(BaseModel):
    title: Optional[str] = None
    priority: Optional[int] = None
    status: Optional[str] = None
    memo: Optional[str] = None
    deadline: Optional[date] = None


class AlwaysTaskOut(BaseModel):
    id: int
    title: str
    priority: int
    status: str
    memo: Optional[str]
    deadline: Optional[date]
    model_config = {"from_attributes": True}


# ── Calendar event ──────────────────────────────────────────────────────────

class CalendarEventCreate(BaseModel):
    event_date: date
    title: str
    memo: Optional[str] = None


class CalendarEventUpdate(BaseModel):
    title: Optional[str] = None
    memo: Optional[str] = None
    event_date: Optional[date] = None


class CalendarEventOut(BaseModel):
    id: int
    event_date: date
    title: str
    memo: Optional[str]
    model_config = {"from_attributes": True}


# ── Dashboard ───────────────────────────────────────────────────────────────

class SectionProgress(BaseModel):
    total: int
    checked: int


class DashboardTaskItem(BaseModel):
    id: int
    type: str
    title: str
    is_urgent: bool
    deadline: Optional[date] = None
    priority: Optional[int] = None
    status: Optional[str] = None


class DashboardOut(BaseModel):
    today: str
    current_period: str
    daily: SectionProgress
    month_start: SectionProgress
    month_end: SectionProgress
    weekly: SectionProgress
    always: SectionProgress
    items: List[DashboardTaskItem]


# ── Bulk import (always tasks) ──────────────────────────────────────────────

class BulkImportRequest(BaseModel):
    text: str


class BulkPreviewLine(BaseModel):
    title: str
    priority: int
    deadline: Optional[date]
    memo: Optional[str]


class BulkPreviewResponse(BaseModel):
    preview: List[BulkPreviewLine]
    count: int
