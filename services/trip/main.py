from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import Base
import crud, schemas

Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

@app.post("/trip/", response_model=schemas.TripOut)
def create_trip(trip: schemas.TripCreate, db: Session = Depends(get_db)):
    return crud.create_trip(db, trip)

@app.get("/trip/{trip_id}", response_model=schemas.TripOut)
def get_trip(trip_id: int, db: Session = Depends(get_db)):
    return crud.get_trip(db, trip_id)

@app.put("/trip/{trip_id}/status", response_model=schemas.TripOut)
def update_trip_status(trip_id: int, status: schemas.StatusUpdate, db: Session = Depends(get_db)):
    return crud.update_status(db, trip_id, status.status)
