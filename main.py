from fastapi import FastAPI, Depends, Request, Form
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
import models, schemas
from database import engine, SessionLocal, Base
from passlib.hash import pbkdf2_sha256
from fastapi.templating import Jinja2Templates


app = FastAPI()

Base.metadata.create_all(bind=engine)

templates = Jinja2Templates(directory="templates")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/register", response_class=HTMLResponse)
def register_get(request: Request):
    return templates.TemplateResponse("register.html", {"request":request})

@app.post("/register", response_class=HTMLResponse)
def register_post(request: Request, username:str = Form(...), 
                  age: int = Form(...), password: str=Form(...), db: Session = Depends(get_db)):
    hash = pbkdf2_sha256.hash(password)
    db_user = models.User(username=username, age=age, password=hash)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    users = db.query(models.User).all()
    return templates.TemplateResponse("users.html", {"request":request, "users":users})

@app.get("/users")
def list_users(request: Request, db: Session = Depends(get_db)):
    users = db.query(models.User).all()
    return templates.TemplateResponse("users.html", {"request": request, "users":users})


@app.get("/", response_class=HTMLResponse)
def read_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/hello", response_class=HTMLResponse)
def read_hello(request: Request, name: str = Form(...)):
    return templates.TemplateResponse("hello.html", {"request":request, "name":name})

@app.post("/users/", response_model=schemas.UserResponse)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    hash = pbkdf2_sha256.hash(user.password_hash)
    db_user = models.User(username=user.username, age=user.age, password_hash=hash)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.get("/users/", response_model=list[schemas.UserResponse])
def read_users(db: Session = Depends(get_db)):
    return db.query(models.User).all()


@app.get("/login/{username}.{password}")
def get_login(username:str, password:str, db: Session = Depends(get_db)):
    db_user = db.get()
    