from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from database import Base


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    todos = relationship("ToDoItem", back_populates="owner", cascade="all, delete-orphan")

class ToDoItem(Base):
    __tablename__ = 'todoitem'

    id = Column(Integer, primary_key=True, index=True)
    description = Column(String, index=True, nullable=False)
    completed = Column(Boolean, default=False)

    owner_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    owner = relationship("User", back_populates="todos")