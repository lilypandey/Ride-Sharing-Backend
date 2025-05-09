# models.py
from sqlalchemy import Column, Integer, String, Enum, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
import enum
from datetime import datetime

Base = declarative_base()

class RideStatus(str, enum.Enum):
    requested = "requested"
    accepted = "accepted"
    ongoing = "ongoing"
    completed = "completed"

class Trip(Base):
    __tablename__ = "trips"
    
    id = Column(Integer, primary_key=True, index=True)
    rider_id = Column(String, nullable=False)
    driver_id = Column(String, nullable=True)
    origin = Column(String, nullable=False)
    destination = Column(String, nullable=False)
    status = Column(Enum(RideStatus), default=RideStatus.requested)
    fare = Column(Float, default=0.0)
    timestamp = Column(DateTime, default=datetime.utcnow)
