from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.auth import LoginRequest, RefreshRequest, AuthResponse, TokenResponse
from app.schemas.user import UserCreate, UserResponse
from app.services import auth_service

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/register", response_model=AuthResponse, status_code=201)
async def register(body: UserCreate, db: AsyncSession = Depends(get_db)):
    user, access_token, refresh_token = await auth_service.register_user(
        db, username=body.username, email=body.email, password=body.password
    )
    return AuthResponse(
        user=UserResponse.model_validate(user),
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post("/login", response_model=AuthResponse)
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    user, access_token, refresh_token = await auth_service.authenticate_user(
        db, username=body.username, password=body.password
    )
    return AuthResponse(
        user=UserResponse.model_validate(user),
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh(body: RefreshRequest, db: AsyncSession = Depends(get_db)):
    access_token, refresh_token = await auth_service.refresh_access_token(db, body.refresh_token)
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)

