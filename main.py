from fastapi import FastAPI, Depends, Request, Form
from fastapi.responses import HTMLResponse
from fastapi import HTTPException
from sqlalchemy.orm import Session
import models, schemas
from database import engine, SessionLocal, Base
from passlib.hash import pbkdf2_sha256
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="somethinglongenought")

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
def register_user(
    request: Request,
    username: str = Form(...),
    age: int = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    repeat = db.query(models.User).filter(models.User.username == username).first()
    if repeat is not None:
        return templates.TemplateResponse("loginerror.html", {"request": request})
    
    hashed_password = pbkdf2_sha256.hash(password)
    db_user = models.User(username=username, age=age, password=hashed_password, role='customer')
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    request.session["username"] = db_user.username  # залогиним сразу после регистрации
    return templates.TemplateResponse("profile.html", {"request": request, "user": db_user})


@app.get("/admin", response_class=HTMLResponse)
def admin_panel(request: Request, db: Session = Depends(get_db)):
    role = request.session.get("role")
    if role != "admin":
        raise HTTPException(status_code=403, detail="Access forbidden") 
    
    users = db.query(models.User).all()
    return templates.TemplateResponse("admin.html", {"request": request, "users": users})


@app.post("/admin/change_role", response_class=HTMLResponse)
def change_role(
    request: Request,
    user_id: int = Form(...),
    new_role: str = Form(...),
    db: Session = Depends(get_db)
):
    if request.session.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Access forbidden")

    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.role = new_role
    db.commit()
    db.refresh(user)

    users = db.query(models.User).all()
    return templates.TemplateResponse("admin.html", {"request": request, "users": users})



@app.get("/users")
def list_users(request: Request, db: Session = Depends(get_db)):
    users = db.query(models.User).all()
    return templates.TemplateResponse("users.html", {"request": request, "users":users})

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/hello", response_class=HTMLResponse)
def read_hello(request: Request, name: str = Form(...)):
    return templates.TemplateResponse("hello.html", {"request":request, "name":name})

@app.post("/users/", response_model=schemas.UserResponse)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    hash = pbkdf2_sha256.hash(user.password)
    db_user = models.User(username=user.username, age=user.age, password=hash)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.get("/users/", response_model=list[schemas.UserResponse])
def read_users(db: Session = Depends(get_db)):
    return db.query(models.User).all()


@app.get("/login", response_class=HTMLResponse)
def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login", response_class=HTMLResponse)
def login_user(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.username == username).first()
    if user and pbkdf2_sha256.verify(password, user.password):
        request.session["username"] = username
        request.session["role"] = user.role
        return templates.TemplateResponse("profile.html", {"request": request, "user": user})
    else:
        return templates.TemplateResponse("loginerror.html", {"request": request})
    
@app.get("/profile", response_class=HTMLResponse)
def profile_page(request: Request, db: Session = Depends(get_db)):
    username = request.session.get("username")
    if not username:
        return templates.TemplateResponse("loginerror.html", {"request": request})

    user = db.query(models.User).filter(models.User.username == username).first()
    return templates.TemplateResponse("profile.html", {"request": request, "user": user})

@app.post("/logout", response_class=HTMLResponse)
def logout(request: Request):
    request.session.clear()
    return templates.TemplateResponse("login.html", {"request": request})
