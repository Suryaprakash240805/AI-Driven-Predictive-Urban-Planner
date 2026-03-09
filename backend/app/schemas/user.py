from pydantic import BaseModel, EmailStr
from uuid import UUID
from app.models.user import UserRole

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: UserRole = UserRole.citizen
    city: str | None = None
    state: str | None = None

class UserOut(BaseModel):
    id: UUID
    name: str
    email: EmailStr
    role: UserRole
    city: str | None
    state: str | None
    is_active: bool
    model_config = {"from_attributes": True}

class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    role: UserRole

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut
