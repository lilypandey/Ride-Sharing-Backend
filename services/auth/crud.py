from sqlalchemy.orm import Session
import models, schemas, utils

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    # create user row
    hashed_pw = utils.hash_password(user.password)
    db_user = models.User(email=user.email, password=hashed_pw, role=user.role)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    # create role-specific details
    if user.role == schemas.UserRole.rider:
        rider = models.Rider(user_id=db_user.id, name=user.name, contact=user.contact)
        db.add(rider)
    else:
        driver = models.Driver(user_id=db_user.id, name=user.name, contact=user.contact, vehicle=user.vehicle or "", status="offline")
        db.add(driver)

    db.commit()
    return db_user
