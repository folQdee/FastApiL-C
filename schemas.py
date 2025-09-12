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

