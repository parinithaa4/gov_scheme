from sqlalchemy import Column, Integer, String, DateTime, Float
from sqlalchemy.sql import func
from database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Scheme(Base):
    __tablename__ = "schemes"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    category = Column(String, index=True)
    eligibility = Column(String)
    state = Column(String, index=True)
    benefits = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class UserResponse(Base):
    __tablename__ = "user_responses"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    age = Column(Integer)
    gender = Column(String)
    occupation = Column(String)
    income = Column(Float)
    state = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())