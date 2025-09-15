from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import jwt, JWTError
import models, schemas, crud, database, oauth2, utils
from database import SessionLocal, engine

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Auth Service")

# Dependency for DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Registration
@app.post("/register/rider", response_model=schemas.UserOut)
def register_rider(user: schemas.RiderCreate, db: Session = Depends(get_db)):
    existing = crud.get_user_by_contact(db, contact=user.contact)
    if existing:
        raise HTTPException(status_code=400, detail="Contact already registered")
    created = crud.create_rider(db, user)
    # Return user + name (via orm_mode)
    return schemas.UserOut(
        id=created.id,
        contact=created.contact,
        role=created.role,
        name=user.name
    )


@app.post("/register/driver", response_model=schemas.UserOut)
def register_driver(user: schemas.DriverCreate, db: Session = Depends(get_db)):
    existing = crud.get_user_by_contact(db, contact=user.contact)
    if existing:
        raise HTTPException(status_code=400, detail="Contact already registered")
    created = crud.create_driver(db, user)
    return schemas.UserOut(
        id=created.id,
        contact=created.contact,
        role=created.role,
        name=user.name
    )


# Login
@app.post("/login", response_model=schemas.Token)
def login(
    user_credentials: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    # OAuth2 form sends username instead of contact → map it
    user = crud.get_user_by_contact(db, contact=user_credentials.username)
    if not user or not utils.verify_password(user_credentials.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid Credentials"
        )
    access_token = oauth2.create_access_token(
        data={"user_id": user.id, "role": user.role.value}
    )
    return {"access_token": access_token, "token_type": "bearer"}


# Current User
@app.get("/me", response_model=schemas.UserOut)
def read_me(current_user: schemas.TokenData = Depends(oauth2.get_current_user), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == current_user.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Mapping back Rider/Driver name
    name = None
    if user.role.value == "rider" and user.rider:
        name = user.rider.name
    elif user.role.value == "driver" and user.driver:
        name = user.driver.name

    return schemas.UserOut(
        id=user.id,
        contact=user.contact,
        role=user.role,
        name=name
    )
