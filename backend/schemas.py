from pydantic import BaseModel


class UserCreate(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class ToDoItemCreate(BaseModel):
    description: str

class ToDoItemResponse(BaseModel):
    id: int
    description: str
    completed: bool
    owner_id: int

    class Config:
        from_attributes = True