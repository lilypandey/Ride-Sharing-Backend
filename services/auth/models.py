from sqlalchemy import Column, Integer, String, Enum, ForeignKey, Float
from sqlalchemy.orm import relationship
from database import Base
import enum


# Role Enum
class UserRole(str, enum.Enum):
    rider = "rider"
    driver = "driver"


# Base User Table
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    contact = Column(String, unique=True, index=True, nullable=False)  # replacing email
    password = Column(String, nullable=False)
    role = Column(Enum(UserRole), nullable=False)

    # One-to-one relationships
    rider = relationship("Rider", back_populates="user", uselist=False)
    driver = relationship("Driver", back_populates="user", uselist=False)


# Rider Table
class Rider(Base):
    __tablename__ = "riders"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    
    user = relationship("User", back_populates="rider")
    
    # Rider-specific fields
    name = Column(String, nullable=False)


# Driver Table
class Driver(Base):
    __tablename__ = "drivers"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    
    user = relationship("User", back_populates="driver")
    
    # Driver-specific fields
    name = Column(String, nullable=False)
    vehicle_license = Column(String, nullable=False)  # required at registration
    status = Column(String, default="offline")        # online/offline
    latitude = Column(Float, nullable=True)           # current location
    longitude = Column(Float, nullable=True)
