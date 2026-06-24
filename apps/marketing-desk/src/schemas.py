from datetime import date
from typing import Optional
from pydantic import BaseModel


class Step0ItemCreate(BaseModel):
    title: str
    memo: Optional[str] = None


class Step0ItemUpdate(BaseModel):
    title: Optional[str] = None
    memo: Optional[str] = None
    is_checked: Optional[bool] = None
    order: Optional[int] = None


class Step0ItemOut(BaseModel):
    id: int
    title: str
    memo: Optional[str]
    is_checked: bool
    order: int
    model_config = {"from_attributes": True}


class WeeklyRoutineCreate(BaseModel):
    title: str
    memo: Optional[str] = None


class WeeklyRoutineUpdate(BaseModel):
    title: Optional[str] = None
    memo: Optional[str] = None
    is_checked: Optional[bool] = None
    order: Optional[int] = None


class WeeklyRoutineOut(BaseModel):
    id: int
    title: str
    memo: Optional[str]
    is_checked: bool
    order: int
    model_config = {"from_attributes": True}


class MonthlyRoutineCreate(BaseModel):
    title: str
    memo: Optional[str] = None
    group: str


class MonthlyRoutineUpdate(BaseModel):
    title: Optional[str] = None
    memo: Optional[str] = None
    is_checked: Optional[bool] = None
    group: Optional[str] = None
    order: Optional[int] = None


class MonthlyRoutineOut(BaseModel):
    id: int
    title: str
    memo: Optional[str]
    group: str
    is_checked: bool
    order: int
    model_config = {"from_attributes": True}


class ImmediateTaskCreate(BaseModel):
    title: str
    deadline: Optional[date] = None
    priority: int = 3
    status: str = "pending"
    memo: Optional[str] = None


class ImmediateTaskUpdate(BaseModel):
    title: Optional[str] = None
    deadline: Optional[date] = None
    priority: Optional[int] = None
    status: Optional[str] = None
    memo: Optional[str] = None


class ImmediateTaskOut(BaseModel):
    id: int
    title: str
    deadline: Optional[date]
    priority: int
    status: str
    memo: Optional[str]
    model_config = {"from_attributes": True}


class BulkImportRequest(BaseModel):
    text: str


class BulkPreviewLine(BaseModel):
    title: str
    priority: int
    deadline: Optional[date]
    memo: Optional[str]


class BulkPreviewResponse(BaseModel):
    preview: list[BulkPreviewLine]
    count: int


class DashboardSection(BaseModel):
    total: int
    checked: int


class DashboardItem(BaseModel):
    id: int
    type: str
    title: str
    is_urgent: bool
    group: Optional[str] = None
    deadline: Optional[date] = None
    priority: Optional[int] = None
    status: Optional[str] = None


class DashboardOut(BaseModel):
    items: list[DashboardItem]
    step0: DashboardSection
    weekly: DashboardSection
    monthly: DashboardSection
    immediate: DashboardSection
    current_period: str
