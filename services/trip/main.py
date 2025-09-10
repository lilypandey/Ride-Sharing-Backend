from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import Base, engine, get_db
import crud, schemas, models
import asyncio
from kafka_consumer import consume_matches
from kafka_producer import publish_trip_request

Base.metadata.create_all(bind=engine)

app = FastAPI(title="trip-service")

@app.post("/trip/", response_model=schemas.TripOut)
async def create_trip(trip: schemas.TripCreate, db: Session = Depends(get_db)):
    new_trip = crud.create_trip(db, trip)

    # Publish trip request to Kafka
    payload = {
        "trip_id": new_trip.id,
        "rider_id": new_trip.rider_id,
        "pickup_lat": trip.origin.split(",")[0],   # Example parsing, replace with real coords
        "pickup_lng": trip.origin.split(",")[1],
        "destination": trip.destination
    }
    await publish_trip_request(payload)

    return new_trip

@app.get("/trip/{trip_id}", response_model=schemas.TripOut)
def get_trip(trip_id: int, db: Session = Depends(get_db)):
    trip = crud.get_trip(db, trip_id)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    return trip

@app.put("/trip/{trip_id}/status", response_model=schemas.TripOut)
def update_trip_status(trip_id: int, status: schemas.StatusUpdate, db: Session = Depends(get_db)):
    trip = crud.update_status(db, trip_id, status.status)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    return trip

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(consume_matches())
