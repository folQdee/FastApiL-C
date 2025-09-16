from sqlalchemy import Column, Integer, String, ForeignKey, Enum
from sqlalchemy.orm import relationship
from database import Base
import enum

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
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)  # 1 к 1 
    specialization = Column(String)
    experience = Column(String)
    price = Column(String)
    description = Column(String)

    user = relationship("User", back_populates="profile")
    orders = relationship("Order", back_populates="engineer") 


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    full_name = Column(String)
    contact = Column(String)
    description = Column(String)

    user = relationship("User", back_populates="customer_profile")
    orders = relationship("Order", back_populates="customer")
    

class OrderStatus(enum.Enum):
    created = "создано"
    in_progress = "в работе"
    paid = "оплачено"


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)

    # связи
    engineer_id = Column(Integer, ForeignKey("engineers.id"))
    customer_id = Column(Integer, ForeignKey("customers.id"))

    # данные заказа
    service_name = Column(String, nullable=False)
    price = Column(Integer, nullable=False)
    status = Column(Enum(OrderStatus), default=OrderStatus.created)

    # отношения
    engineer = relationship("SoundEngineer", back_populates="orders")
    customer = relationship("Customer", back_populates="orders")