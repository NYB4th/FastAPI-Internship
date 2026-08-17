from database import Base
from sqlalchemy import Column, Integer, String


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, index=True)
    description = Column(String, nullable=True)
    priority = Column(Integer, nullable=False, default=1)
    status = Column(String, nullable=False, default="pending")
