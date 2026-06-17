from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from .database import Base


def utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)


class TaskCategory(Base):
    __tablename__ = "task_categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    created_at = Column(DateTime, default=utcnow)
    tasks = relationship("Task", back_populates="category")
    templates = relationship("TaskTemplate", back_populates="category")


class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    category_id = Column(Integer, ForeignKey("task_categories.id"), nullable=True)
    priority = Column(Integer, default=3)  # 1-5
    status = Column(String(20), default="pending")  # pending / in_progress / done
    deadline = Column(Date, nullable=True)
    recurrence = Column(String(20), nullable=True)  # daily / weekly / None
    memo = Column(Text, nullable=True)
    source = Column(String(10), nullable=True, default="직접")  # 반복 / 직접
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)
    category = relationship("TaskCategory", back_populates="tasks")


class TaskTemplate(Base):
    __tablename__ = "task_templates"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    category_id = Column(Integer, ForeignKey("task_categories.id"), nullable=True)
    default_priority = Column(Integer, default=3)
    deadline_offset_days = Column(Integer, nullable=True)  # days to add to today
    created_at = Column(DateTime, default=utcnow)
    category = relationship("TaskCategory", back_populates="templates")
