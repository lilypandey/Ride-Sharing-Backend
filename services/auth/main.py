from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import jwt, JWTError
import models, schemas, crud, database, oauth2, utils
from database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="auth")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/register", response_model=schemas.UserOut)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = crud.get_user_by_email(db, email=user.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    created = crud.create_user(db, user)
    return created

@app.post("/login", response_model=schemas.Token)
def login(user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, email=user_credentials.username)
    if not user or not utils.verify_password(user_credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials")
    access_token = oauth2.create_access_token(data={"user_id": user.id, "role": user.role.value})
    refresh_token = oauth2.create_refresh_token(data={"user_id": user.id, "role": user.role.value})
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@app.post("/refresh", response_model=schemas.Token)
def refresh_token(refresh_token: str, db: Session = Depends(get_db)):
    # validate refresh token & issue new tokens
    try:
        payload = jwt.decode(refresh_token, oauth2.SECRET_KEY, algorithms=[oauth2.ALGORITHM])
        user_id = payload.get("user_id")
        role = payload.get("role")
        if user_id is None or role is None:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    new_access = oauth2.create_access_token(data={"user_id": user.id, "role": user.role.value})
    new_refresh = oauth2.create_refresh_token(data={"user_id": user.id, "role": user.role.value})
    return {"access_token": new_access, "refresh_token": new_refresh, "token_type": "bearer"}

@app.get("/me")
def read_me(current_user = Depends(oauth2.get_current_user), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == current_user["user_id"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"id": user.id, "email": user.email, "role": user.role.value}

