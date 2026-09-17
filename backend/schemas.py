from pydantic import BaseModel

class ToDoItemCreate(BaseModel):
    description: str

class ToDoItemResponse(BaseModel):
    id: int
    description: str
    completed: bool

    class Config:
        from_attributes = True