from sqlalchemy.orm import Session
from models import Trip, RideStatus
from schemas import TripCreate


def create_trip(db: Session, trip: TripCreate) -> Trip:
    db_trip = Trip(
        rider_id=trip.rider_id,
        origin=trip.origin,
        destination=trip.destination,
    )
    db.add(db_trip)
    db.commit()
    db.refresh(db_trip)
    return db_trip


def get_trip(db: Session, trip_id: int) -> Trip:
    return db.query(Trip).filter(Trip.id == trip_id).first()


def update_status(db: Session, trip_id: int, new_status: RideStatus) -> Trip:
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if trip:
        trip.status = new_status
        db.commit()
        db.refresh(trip)
    return trip