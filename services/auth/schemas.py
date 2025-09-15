from pydantic import BaseModel
from enum import Enum


# Role Enum
class UserRole(str, Enum):
    rider = "rider"
    driver = "driver"


# Registration Schemas
class RiderCreate(BaseModel):
    contact: str
    password: str
    role: UserRole = UserRole.rider   # fixed to rider
    name: str


class DriverCreate(BaseModel):
    contact: str
    password: str
    role: UserRole = UserRole.driver  # fixed to driver
    name: str
    vehicle_license: str              # required for drivers


# Login Schema
class UserLogin(BaseModel):
    contact: str
    password: str


# Token Schemas
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: int
    role: str


# Output Schema
class UserOut(BaseModel):
    id: int
    contact: str
    role: UserRole
    name: str

    class Config:
        orm_mode = True

