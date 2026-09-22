from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, EmailStr, ConfigDict

class LoginRequest(BaseModel):
    username_or_email: str = Field(..., description="Farmer email or registered phone number")
    password: str = Field(..., min_length=4, description="Farmer password or security PIN")

class RegisterRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=30)
    password: str = Field(..., min_length=6)
    address: Optional[str] = Field(None, max_length=255)

class FarmerUser(BaseModel):
    id: int
    name: str
    email: str
    phone: Optional[str] = None
    address: Optional[str] = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class AuthResponse(BaseModel):
    success: bool
    message: str
    access_token: Optional[str] = None
    token_type: str = "bearer"
    farmer: Optional[FarmerUser] = None
