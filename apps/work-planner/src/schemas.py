from datetime import date
from typing import Optional
from pydantic import BaseModel, Field


# TaskCategory
class TaskCategoryBase(BaseModel):
    name: str

class TaskCategoryCreate(TaskCategoryBase):
    pass

class TaskCategoryUpdate(TaskCategoryBase):
    pass

class TaskCategoryOut(TaskCategoryBase):
    id: int
    model_config = {"from_attributes": True}


# Task
class TaskBase(BaseModel):
    title: str
    category_id: Optional[int] = None
    clinic: Optional[str] = None
    priority: int = Field(default=3, ge=1, le=5)
    due_date: Optional[date] = None
    status: str = "대기"
    memo: Optional[str] = None

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    category_id: Optional[int] = None
    clinic: Optional[str] = None
    priority: Optional[int] = Field(default=None, ge=1, le=5)
    due_date: Optional[date] = None
    status: Optional[str] = None
    memo: Optional[str] = None

class TaskOut(TaskBase):
    id: int
    category: Optional[TaskCategoryOut] = None
    model_config = {"from_attributes": True}


# TaskTemplate
class TaskTemplateBase(BaseModel):
    title: str
    category_id: Optional[int] = None
    default_priority: int = Field(default=3, ge=1, le=5)

class TaskTemplateCreate(TaskTemplateBase):
    pass

class TaskTemplateUpdate(TaskTemplateBase):
    title: Optional[str] = None
    default_priority: Optional[int] = Field(default=None, ge=1, le=5)

class TaskTemplateOut(TaskTemplateBase):
    id: int
    category: Optional[TaskCategoryOut] = None
    model_config = {"from_attributes": True}


# Summary
class SummaryOut(BaseModel):
    today_count: int
    overdue_count: int
    in_progress_count: int
