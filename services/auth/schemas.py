from pydantic import BaseModel
from typing import Optional
from enum import Enum

class UserRole(str, Enum):
    rider = "rider"
    driver = "driver"

class UserCreate(BaseModel):
    email: str
    password: str
    role: UserRole
    name: str
    contact: str
    vehicle: Optional[str] = None  # only for drivers

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: int
    role: str

class UserOut(BaseModel):
    id: int
    email: str
    role: UserRole

    class Config:
        orm_mode = True

