from fastapi import FastAPI, Depends, HTTPException
import models, database, crud, schemas
from sqlalchemy.orm import Session
import time
from sqlalchemy.exc import OperationalError

app = FastAPI()

# Trying to connect with retries
MAX_TRIES = 5
for i in range(MAX_TRIES):
    try:
        models.Base.metadata.create_all(bind=database.engine)
        break
    except OperationalError:
        print(f"Database not ready yet. Waiting... {i+1}/{MAX_TRIES}")
        time.sleep(2)
else:
    print("Database connection failed after retries. Exiting.")
    exit(1)

@app.post("/register")
def register_user(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db, user)
