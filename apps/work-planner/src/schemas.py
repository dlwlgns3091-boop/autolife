from datetime import date
from typing import Optional
from pydantic import BaseModel, Field


# Category
class CategoryCreate(BaseModel):
    name: str

class CategoryUpdate(BaseModel):
    name: str

class CategoryOut(BaseModel):
    id: int
    name: str
    model_config = {"from_attributes": True}


# Task
class TaskCreate(BaseModel):
    title: str
    category_id: Optional[int] = None
    priority: int = Field(default=3, ge=1, le=5)
    status: str = "pending"
    deadline: Optional[date] = None
    recurrence: Optional[str] = None  # daily / weekly
    memo: Optional[str] = None

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    category_id: Optional[int] = None
    priority: Optional[int] = Field(default=None, ge=1, le=5)
    status: Optional[str] = None
    deadline: Optional[date] = None
    recurrence: Optional[str] = None
    memo: Optional[str] = None

class TaskOut(BaseModel):
    id: int
    title: str
    category_id: Optional[int] = None
    category_name: Optional[str] = None
    priority: int
    status: str
    deadline: Optional[date] = None
    recurrence: Optional[str] = None
    memo: Optional[str] = None
    model_config = {"from_attributes": True}

class BulkTaskLine(BaseModel):
    title: str
    category_name: Optional[str] = None
    priority: int = 3
    deadline: Optional[date] = None
    memo: Optional[str] = None

class BulkPreviewResponse(BaseModel):
    preview: list[BulkTaskLine]
    count: int

class BulkCreateRequest(BaseModel):
    text: str


# Template
class TemplateCreate(BaseModel):
    title: str
    category_id: Optional[int] = None
    default_priority: int = Field(default=3, ge=1, le=5)
    deadline_offset_days: Optional[int] = None

class TemplateUpdate(BaseModel):
    title: Optional[str] = None
    category_id: Optional[int] = None
    default_priority: Optional[int] = Field(default=None, ge=1, le=5)
    deadline_offset_days: Optional[int] = None

class TemplateOut(BaseModel):
    id: int
    title: str
    category_id: Optional[int] = None
    category_name: Optional[str] = None
    default_priority: int
    deadline_offset_days: Optional[int] = None
    model_config = {"from_attributes": True}


# Summary
class SummaryOut(BaseModel):
    today_count: int
    overdue_count: int
    in_progress_count: int
