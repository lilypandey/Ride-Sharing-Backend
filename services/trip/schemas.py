from pydantic import BaseModel
from enum import Enum

class RideStatus(str, Enum):
    requested = "requested"
    accepted = "accepted"
    ongoing = "ongoing"
    completed = "completed"

class TripCreate(BaseModel):
    rider_id: str
    origin: str
    destination: str

class TripOut(TripCreate):
    id: int
    status: RideStatus
    fare: float
    driver_id: str | None

    class Config:
        orm_mode = True

class StatusUpdate(BaseModel):
    status: RideStatus

