from fastapi import FastAPI, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
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


#ЗВУКОРЕЖИССЕРЫ
@app.get("/profile/edit", response_class=HTMLResponse)
def edit_profile(request: Request, db: Session = Depends(get_db)):
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")

    profile = db.query(models.SoundEngineer).filter(models.SoundEngineer.user_id == user_id).first()
    return templates.TemplateResponse("user/edit_profile.html", {"request": request, "profile": profile})


@app.post("/profile/edit", response_class=HTMLResponse)
def save_profile(
    request: Request,
    specialization: str = Form(...),
    experience: str = Form(...),
    price: str = Form(...),
    description: str = Form(...),
    db: Session = Depends(get_db)
):
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")

    profile = db.query(models.SoundEngineer).filter(models.SoundEngineer.user_id == user_id).first()
    if profile:
        # обновляем
        profile.specialization = specialization
        profile.experience = experience
        profile.price = price
        profile.description = description
    else:
        # создаём новый
        profile = models.SoundEngineer(
            user_id=user_id,
            specialization=specialization,
            experience=experience,
            price=price,
            description=description,
        )
        db.add(profile)

    db.commit()
    db.refresh(profile)

    return templates.TemplateResponse("profile.html", {"request": request, "user": profile.user})


#РЕГИСТРАЦИЯ
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

#АДМИН
@app.get("/admin", response_class=HTMLResponse)
def admin_panel(request: Request, db: Session = Depends(get_db)):
    role = request.session.get("role")
    if role != "admin":
        raise HTTPException(status_code=403, detail="Access forbidden") 
    
    users = db.query(models.User).all()
    return templates.TemplateResponse("admin/admin.html", {"request": request, "users": users})


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
    return templates.TemplateResponse("admin/admin.html", {"request": request, "users": users})



@app.get("/users")
def list_users(request: Request, db: Session = Depends(get_db)):
    users = db.query(models.User).all()
    return templates.TemplateResponse("users.html", {"request": request, "users":users})

# ГЛАВНАЯ СТРАНИЦА
@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    username = request.session.get("username")
    if not username:
        return templates.TemplateResponse("user/unauth_main_page.html", {"request":request})
    
    return templates.TemplateResponse("user/auth_main_page.html", {"request": request})


#ЛОГИН
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
        request.session["user_id"] = user.id 
        request.session["role"] = user.role 
        return templates.TemplateResponse("profile.html", {"request": request, "user": user})
    else:
        return templates.TemplateResponse("loginerror.html", {"request": request})

    

@app.post("/logout", response_class=HTMLResponse)
def logout(request: Request):
    request.session.clear()
    return RedirectResponse('/', 303)
    
#ПРОФИЛЬ
@app.get("/profile", response_class=HTMLResponse)
def profile_page(request: Request, db: Session = Depends(get_db)):
    username = request.session.get("username")
    if not username:
        return templates.TemplateResponse("user/unauth_profile.html", {"request": request})

    user = db.query(models.User).filter(models.User.username == username).first()
    return templates.TemplateResponse("profile.html", {"request": request, "user": user})

#РЕДАКТИРОВАНИЕ ПРОФИЛЯ
@app.get("/profile/edit", response_class=HTMLResponse)
def edit_profile(request: Request, db: Session = Depends(get_db)):
    user_id = request.session.get("user_id")
    role = request.session.get("role")

    if not user_id:
        return templates.TemplateResponse("login.html", {"request": request})

    profile = None
    if role == "sound_engineer":
        profile = db.query(models.SoundEngineer).filter(models.SoundEngineer.user_id == user_id).first()
    elif role == "customer":
        profile = db.query(models.Customer).filter(models.Customer.user_id == user_id).first()

    return templates.TemplateResponse(
        "user/edit_profile.html",
        {"request": request, "profile": profile, "role": role}
    )

@app.post("/profile/edit", response_class=HTMLResponse)
def save_profile(
    request: Request,
    specialization: str = Form(None),
    experience: str = Form(None),
    price: str = Form(None),
    description: str = Form(None),
    full_name: str = Form(None),
    contact: str = Form(None),
    db: Session = Depends(get_db)
):
    user_id = request.session.get("user_id")
    role = request.session.get("role")

    if not user_id:
        raise HTTPException(status_code=403, detail="Not Authorized")
    
    if role == "sound_engineer":
        profile = db.query(models.SoundEngineer).filter_by(user_id=user_id).first()
        if not profile:
            profile = models.SoundEngineer(user_id=user_id)
            db.add(profile)

        profile.specialization = specialization
        profile.experience = experience
        profile.price = price
        profile.description = description


    elif role == "customer":
        profile = db.query(models.Customer).filter_by(user_id=user_id).first()
        if not profile:
            profile = models.Customer(user_id=user_id)
            db.add(profile)

        profile.full_name = full_name
        profile.contact = contact
        profile.description = description
    
    else:
        raise HTTPException(403, "forbidden")
    
    db.commit()
    db.refresh(profile)
    
    return templates.TemplateResponse("profile.html", {"request": request, "user": profile.user})

