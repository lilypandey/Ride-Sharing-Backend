from sqlalchemy.orm import Session
from models import Trip, RideStatus
from schemas import TripCreate

def create_trip(db: Session, trip: TripCreate, rider_id: str) -> Trip:
    db_trip = Trip(
        rider_id=rider_id,
        origin=trip.origin,
        destination=trip.destination,
        status=RideStatus.requested
    )
    db.add(db_trip)
    db.commit()
    db.refresh(db_trip)
    return db_trip

def get_trip(db: Session, trip_id: int) -> Trip | None:
    return db.query(Trip).filter(Trip.id == trip_id).first()

def get_trips_by_rider(db: Session, rider_id: str) -> list[Trip]:
    return db.query(Trip).filter(Trip.rider_id == rider_id).all()

def update_status(db: Session, trip_id: int, new_status: RideStatus) -> Trip | None:
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        return None
    trip.status = new_status
    db.commit()
    db.refresh(trip)
    return trip

def assign_driver(db: Session, trip_id: int, driver_id: str, distance: float) -> Trip | None:
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        return None
    if trip.driver_id:  # already assigned
        return trip
    
    trip.driver_id = driver_id
    trip.status = RideStatus.accepted
    trip.fare = calculate_fare(distance)
    db.commit()
    db.refresh(trip)
    return trip

# helper
def calculate_fare(distance: float) -> float:
    base_fare = 20
    per_km = 10
    return base_fare + (distance * per_km)
