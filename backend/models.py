from sqlalchemy import Column, Integer, String, Boolean
from database import Base

class ToDoItem(Base):
    __tablename__ = 'todoitem'

    id = Column(Integer, primary_key=True, index=True)
    description = Column(String, index=True, nullable=False)
    completed = Column(Boolean, default=False)