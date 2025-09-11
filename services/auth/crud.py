from sqlalchemy.orm import Session
import models, schemas, utils


# Get user by contact
def get_user_by_contact(db: Session, contact: str):
    return db.query(models.User).filter(models.User.contact == contact).first()


# Create Rider
def create_rider(db: Session, user: schemas.RiderCreate):
    # hash password
    hashed_pw = utils.hash_password(user.password)

    # create base User row
    db_user = models.User(
        contact=user.contact,
        password=hashed_pw,
        role=user.role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    # create Rider row linked to User
    rider = models.Rider(
        user_id=db_user.id,
        name=user.name
    )
    db.add(rider)
    db.commit()
    db.refresh(rider)

    return db_user


# Create Driver
def create_driver(db: Session, user: schemas.DriverCreate):
    # hash password
    hashed_pw = utils.hash_password(user.password)

    # create base User row
    db_user = models.User(
        contact=user.contact,
        password=hashed_pw,
        role=user.role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    # create Driver row linked to User
    driver = models.Driver(
        user_id=db_user.id,
        name=user.name,
        vehicle_license=user.vehicle_license,
        status="offline"
    )
    db.add(driver)
    db.commit()
    db.refresh(driver)

    return db_user
