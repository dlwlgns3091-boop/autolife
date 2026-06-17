from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Date, DateTime, Boolean, Text, Numeric
from .database import Base


def utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)


class Todo(Base):
    __tablename__ = "todos"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    priority = Column(Integer, default=3)       # 1–5
    status = Column(String(20), default="pending")  # pending / in_progress / done
    due_date = Column(Date, nullable=True)
    memo = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)


class BudgetCategory(Base):
    __tablename__ = "budget_categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)


class BudgetEntry(Base):
    __tablename__ = "budget_entries"
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False)
    amount = Column(Integer, nullable=False)        # 원 단위 정수
    category_id = Column(Integer, nullable=True)
    entry_type = Column(String(10), nullable=False)  # income / expense
    memo = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utcnow)
