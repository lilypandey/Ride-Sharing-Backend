from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import Base, engine, get_db
import crud, schemas, models
import asyncio
from kafka_consumer import consume_matches
from kafka_producer import publish_trip_request
from oauth2 import get_current_user, TokenData

# Create tables (in production you’d use Alembic instead of auto-create)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="trip-service")

# Create Trip
@app.post("/trip/", response_model=schemas.TripOut)
async def create_trip(
    trip: schemas.TripCreate,
    db: Session = Depends(get_db),
    user: TokenData = Depends(get_current_user)  # TokenData instead of dict
):
    if user.role != "rider":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only riders can create trips"
        )

    new_trip = crud.create_trip(db, trip, user.id)

    # Publish trip request to Kafka
    # Replace parsing with real origin/destination schema (lat/lng fields ideally)
    try:
        pickup_lat, pickup_lng = trip.origin.split(",")
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid origin format. Expected 'lat,lng'"
        )

    payload = {
        "trip_id": new_trip.id,
        "rider_id": new_trip.rider_id,
        "pickup_lat": pickup_lat.strip(),
        "pickup_lng": pickup_lng.strip(),
        "destination": trip.destination
    }
    await publish_trip_request(payload)

    return new_trip


# Get Trip by ID
@app.get("/trip/{trip_id}", response_model=schemas.TripOut)
def get_trip(
    trip_id: int,
    db: Session = Depends(get_db),
    user: TokenData = Depends(get_current_user)
):
    trip = crud.get_trip(db, trip_id)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")

    # ensure only rider who owns the trip can view it
    if trip.rider_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this trip")

    return trip


# Update Trip Status
@app.put("/trip/{trip_id}/status", response_model=schemas.TripOut)
def update_trip_status(
    trip_id: int,
    status: schemas.StatusUpdate,
    db: Session = Depends(get_db),
    user: TokenData = Depends(get_current_user)
):
    trip = crud.get_trip(db, trip_id)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")

    if user.id not in [trip.rider_id, trip.driver_id]:
        raise HTTPException(status_code=403, detail="Not authorized to update this trip")

    updated_trip = crud.update_status(db, trip_id, status.status)
    return updated_trip


# Kafka Consumer Background Task
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(consume_matches())
