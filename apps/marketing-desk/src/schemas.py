from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, field_validator


# --- Step 0 ---
class Step0ItemCreate(BaseModel):
    title: str
    memo: Optional[str] = None
    checked: bool = False


class Step0ItemUpdate(BaseModel):
    title: Optional[str] = None
    memo: Optional[str] = None
    checked: Optional[bool] = None


class Step0ItemOut(BaseModel):
    id: int
    title: str
    memo: Optional[str]
    checked: bool
    sort_order: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# --- Weekly ---
class WeeklyItemCreate(BaseModel):
    title: str
    memo: Optional[str] = None
    checked: bool = False


class WeeklyItemUpdate(BaseModel):
    title: Optional[str] = None
    memo: Optional[str] = None
    checked: Optional[bool] = None


class WeeklyItemOut(BaseModel):
    id: int
    title: str
    memo: Optional[str]
    checked: bool
    sort_order: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# --- Monthly ---
VALID_PERIODS = {"월초", "월중", "월말"}


class MonthlyItemCreate(BaseModel):
    title: str
    memo: Optional[str] = None
    checked: bool = False
    period: str

    @field_validator("period")
    @classmethod
    def validate_period(cls, v: str) -> str:
        if v not in VALID_PERIODS:
            raise ValueError(f"period must be one of {VALID_PERIODS}")
        return v


class MonthlyItemUpdate(BaseModel):
    title: Optional[str] = None
    memo: Optional[str] = None
    checked: Optional[bool] = None
    period: Optional[str] = None

    @field_validator("period")
    @classmethod
    def validate_period(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in VALID_PERIODS:
            raise ValueError(f"period must be one of {VALID_PERIODS}")
        return v


class MonthlyItemOut(BaseModel):
    id: int
    title: str
    memo: Optional[str]
    checked: bool
    period: str
    sort_order: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# --- Immediate ---
class ImmediateTaskCreate(BaseModel):
    title: str
    deadline: Optional[date] = None
    priority: int = 3
    status: str = "pending"
    memo: Optional[str] = None

    @field_validator("priority")
    @classmethod
    def validate_priority(cls, v: int) -> int:
        if not 1 <= v <= 5:
            raise ValueError("priority must be between 1 and 5")
        return v

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        if v not in {"pending", "in_progress", "done"}:
            raise ValueError("status must be pending, in_progress, or done")
        return v


class ImmediateTaskUpdate(BaseModel):
    title: Optional[str] = None
    deadline: Optional[date] = None
    priority: Optional[int] = None
    status: Optional[str] = None
    memo: Optional[str] = None

    @field_validator("priority")
    @classmethod
    def validate_priority(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and not 1 <= v <= 5:
            raise ValueError("priority must be between 1 and 5")
        return v

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in {"pending", "in_progress", "done"}:
            raise ValueError("status must be pending, in_progress, or done")
        return v


class ImmediateTaskOut(BaseModel):
    id: int
    title: str
    deadline: Optional[date]
    priority: int
    status: str
    memo: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
