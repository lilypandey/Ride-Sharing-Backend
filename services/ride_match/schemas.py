from pydantic import BaseModel

class TripRequest(BaseModel):
    trip_id: int
    rider_id: str
    origin_lat: float
    origin_lng: float
    destination: str

class MatchResult(BaseModel):
    trip_id: int
    rider_id: str
    driver_id: str
    distance_km: float
