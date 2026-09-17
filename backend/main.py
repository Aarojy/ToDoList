from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from starlette import status

import models
from auth import (
    create_access_token,
    get_current_user,
    get_password_hash,
    verify_password,
)
from database import engine, get_db
from schemas import ToDoItemCreate, ToDoItemResponse, Token, UserCreate, UserResponse

models.Base.metadata.create_all(bind=engine)
app = FastAPI(title="To-Do Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- AUTH Endpoints ---
@app.post("/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(models.User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    hashed_pwd = get_password_hash(user_data.password)
    new_user = models.User(username=user_data.username, hashed_password=hashed_pwd)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/auth/token", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, str(user.hashed_password)):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

# --- TO-DO Endpoints ---
@app.post("/todos", response_model=ToDoItemResponse)
def create_todo(todo: ToDoItemCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_todo = models.ToDoItem(description=todo.description, owner_id=current_user.id)
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo

@app.get("/todos", response_model=list[ToDoItemResponse])
def read_todos(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return db.query(models.ToDoItem).filter(models.ToDoItem.owner_id == current_user.id).all()

@app.put("/todos/{id}", response_model=ToDoItemResponse)
def toggle_todo(todo_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_todo = (
        db.query(models.ToDoItem).filter(models.ToDoItem.id == todo_id, models.ToDoItem.owner_id == current_user.id).first()
    )

    if not db_todo:
        raise HTTPException(status_code=404, detail="Todo not found")

    db_todo.completed = not db_todo.completed
    db.commit()
    db.refresh(db_todo)
    return db_todo

@app.delete("/todos/{id}")
def delete_todo(todo_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_todo = db.query(models.ToDoItem).filter(models.ToDoItem.id == todo_id, models.ToDoItem.owner_id == current_user.id).first()

    if not db_todo:
        raise HTTPException(status_code=404, detail="Todo not found")

    db.delete(db_todo)
    db.commit()
    return {"message": "Deleted successfully"}