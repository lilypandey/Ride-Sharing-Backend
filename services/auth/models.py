from sqlalchemy import Column, Integer, String, Enum, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
import enum

class UserRole(str, enum.Enum):
    rider = "rider"
    driver = "driver"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(Enum(UserRole), nullable=False)

    rider = relationship("Rider", back_populates="user", uselist=False)
    driver = relationship("Driver", back_populates="user", uselist=False)


class Rider(Base):
    __tablename__ = "riders"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String, nullable=False)
    contact = Column(String, nullable=False)

    user = relationship("User", back_populates="rider")


class Driver(Base):
    __tablename__ = "drivers"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String, nullable=False)
    contact = Column(String, nullable=False)
    vehicle = Column(String, nullable=True)
    status = Column(String, default="offline")

    user = relationship("User", back_populates="driver")
