from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


class UserCreate(BaseModel):
    username: Annotated[str, Field(min_length=1, strip_whitespace=True)]
    password: Annotated[str, Field(min_length=1)]

class UserResponse(BaseModel):
    id: int
    username: str

    model_config = ConfigDict(from_attributes=True)

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

    model_config = ConfigDict(from_attributes=True)