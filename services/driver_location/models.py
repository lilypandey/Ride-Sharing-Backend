from pydantic import BaseModel, Field

class LocationUpdate(BaseModel):
    driver_id: str = Field(..., example="driver_123")
    latitude: float = Field(..., example=19.07)
    longitude: float = Field(..., example=72.87)
