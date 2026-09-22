import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from sqlalchemy import or_

from backend.app.db.session import get_db
from backend.app.models.farmer import Farmer
from backend.app.schemas.auth import LoginRequest, RegisterRequest, AuthResponse, FarmerUser
from backend.app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
    DEFAULT_DEMO_PASSWORD
)

logger = logging.getLogger(__name__)
router = APIRouter()

def get_current_farmer(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> Farmer:
    """Dependency to retrieve authenticated farmer from Bearer token."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authentication token. Please log in.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = authorization.split("Bearer ")[1].strip()
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session has expired or is invalid. Please log in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    farmer_id = int(payload["sub"])
    farmer = db.query(Farmer).filter(Farmer.id == farmer_id).first()
    if not farmer:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authenticated farmer account not found.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return farmer


@router.post("/login", response_model=AuthResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate farmer by Email or Phone number and password."""
    ident = request.username_or_email.strip().lower()

    # Search by email or phone
    farmer = db.query(Farmer).filter(
        or_(
            Farmer.email.ilike(ident),
            Farmer.phone == request.username_or_email.strip()
        )
    ).first()

    if not farmer:
        logger.warning(f"Failed login attempt for nonexistent user: {ident}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email/phone or password. Please verify your credentials."
        )

    if not verify_password(request.password, farmer.password_hash):
        logger.warning(f"Incorrect password attempt for farmer ID {farmer.id} ({farmer.email})")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email/phone or password. Please verify your credentials."
        )

    token = create_access_token({"sub": str(farmer.id), "email": farmer.email, "name": farmer.name})
    logger.info(f"Farmer successfully authenticated: ID {farmer.id} ({farmer.name})")

    return AuthResponse(
        success=True,
        message=f"Welcome back, {farmer.name}!",
        access_token=token,
        token_type="bearer",
        farmer=FarmerUser.model_validate(farmer)
    )


@router.post("/logout", response_model=AuthResponse)
def logout():
    """Client-side session invalidation acknowledgment."""
    return AuthResponse(
        success=True,
        message="Logged out successfully. All local sessions terminated."
    )


@router.get("/me", response_model=AuthResponse)
def get_me(current_farmer: Farmer = Depends(get_current_farmer)):
    """Return currently authenticated farmer profile."""
    return AuthResponse(
        success=True,
        message="Active session verified.",
        farmer=FarmerUser.model_validate(current_farmer)
    )


@router.post("/register", response_model=AuthResponse)
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """Register a new farmer account with securely hashed credentials."""
    existing = db.query(Farmer).filter(Farmer.email == request.email.lower()).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A farmer account with this email address already exists."
        )

    new_farmer = Farmer(
        name=request.name.strip(),
        email=request.email.lower().strip(),
        phone=request.phone.strip() if request.phone else None,
        address=request.address.strip() if request.address else None,
        password_hash=hash_password(request.password)
    )
    db.add(new_farmer)
    db.commit()
    db.refresh(new_farmer)

    token = create_access_token({"sub": str(new_farmer.id), "email": new_farmer.email, "name": new_farmer.name})
    logger.info(f"New farmer account registered: ID {new_farmer.id} ({new_farmer.name})")

    return AuthResponse(
        success=True,
        message="Registration successful! Welcome to KrishiPals.",
        access_token=token,
        token_type="bearer",
        farmer=FarmerUser.model_validate(new_farmer)
    )
