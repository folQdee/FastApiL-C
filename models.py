from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    age = Column(Integer)
    role = Column(String)
    password = Column(String)

    profile = relationship("SoundEngineer", back_populates="user", uselist=False)    
    customer_profile = relationship("Customer", uselist=False, back_populates="user")


class SoundEngineer(Base):
    __tablename__ = "engineers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)  # 1 к 1 связь
    specialization = Column(String)
    experience = Column(String)
    price = Column(String)
    description = Column(String)

    user = relationship("User", back_populates="profile")


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    full_name = Column(String)
    contact = Column(String)
    description = Column(String)

    user = relationship("User", back_populates="customer_profile")
    