from datetime import date
from sqlalchemy import Column, Integer, String, Date, Text, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base


class TaskCategory(Base):
    __tablename__ = "task_categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    tasks = relationship("Task", back_populates="category")
    templates = relationship("TaskTemplate", back_populates="category")


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    category_id = Column(Integer, ForeignKey("task_categories.id"), nullable=True)
    clinic = Column(String(200), nullable=True)
    priority = Column(Integer, nullable=False, default=3)  # 1~5, 5 = highest
    due_date = Column(Date, nullable=True)
    status = Column(String(20), nullable=False, default="대기")  # 대기 / 진행중 / 완료
    memo = Column(Text, nullable=True)

    category = relationship("TaskCategory", back_populates="tasks")


class TaskTemplate(Base):
    __tablename__ = "task_templates"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    category_id = Column(Integer, ForeignKey("task_categories.id"), nullable=True)
    default_priority = Column(Integer, nullable=False, default=3)

    category = relationship("TaskCategory", back_populates="templates")
