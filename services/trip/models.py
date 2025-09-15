from sqlalchemy import Column, Integer, String, Enum, Float, DateTime
from database import Base
from datetime import datetime
import enum

class RideStatus(str, enum.Enum):
    requested = "requested"
    accepted = "accepted"
    ongoing = "ongoing"
    completed = "completed"
    cancelled = "cancelled"

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
