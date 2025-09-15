from pydantic import BaseModel
from enum import Enum
from datetime import datetime

class RideStatus(str, Enum):
    requested = "requested"
    accepted = "accepted"
    ongoing = "ongoing"
    completed = "completed"
    cancelled = "cancelled"

class TripCreate(BaseModel):
    origin: str
    destination: str

class TripOut(BaseModel):
    id: int
    rider_id: str
    driver_id: str | None
    origin: str
    destination: str
    status: RideStatus
    fare: float | None = None
    timestamp: datetime

    class Config:
        orm_mode = True

class StatusUpdate(BaseModel):
    status: RideStatus

