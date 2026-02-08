from sqlmodel import Session, create_engine, select
from src.models.task import Task
import os

DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL)

with Session(engine) as session:
    tasks = session.exec(select(Task)).all()
    print(f"Total tasks: {len(tasks)}")
    for task in tasks:
        print(f"ID: {task.id} | User: {task.user_id} | Title: {task.title} | Priority: {task.priority} | Status: {task.status} | Completed: {task.completed}")
