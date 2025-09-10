from pydantic import BaseModel, Field

class LocationUpdate(BaseModel):
    latitude: float = Field(..., example=19.07)
    longitude: float = Field(..., example=72.87)

class StatusUpdate(BaseModel):
    status: str = Field(..., example="offline")  # available | busy | offline

