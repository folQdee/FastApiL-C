from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    age: int
    password_hash: str


class UserResponse(BaseModel):
    id: int
    username: str
    age: int
    role: str

    class Config:
        orm_mode = True
        

class ProfileCreate(BaseModel):
    specialization: str
    experience: str
    price: str
    description: str

class ProfileResponse(ProfileCreate):
    id: int
    user_id: int

    class Config:
        orm_mode = True
