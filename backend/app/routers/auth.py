from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.config import settings
from app.core.security import create_access_token, create_refresh_token, decode_token
from app.models.user import User
from app.schemas.common import TokenResponse
from app.schemas.user import UserResponse
from app.services.line_auth import exchange_line_code, get_line_profile
import secrets
from urllib.parse import urlencode

router = APIRouter(prefix="/auth", tags=["auth"])


ALLOWED_REDIRECT_URIS = [
    settings.LINE_LOGIN_REDIRECT_URI,
    settings.LINE_ADMIN_REDIRECT_URI,
]


@router.get("/line/login-url")
async def get_line_login_url(redirect_uri: str | None = None):
    """Get LINE Login OAuth URL"""
    uri = redirect_uri or settings.LINE_LOGIN_REDIRECT_URI
    if uri not in ALLOWED_REDIRECT_URIS:
        raise HTTPException(status_code=400, detail="Invalid redirect_uri")
    state = secrets.token_urlsafe(16)
    params = {
        "response_type": "code",
        "client_id": settings.LINE_LOGIN_CHANNEL_ID,
        "redirect_uri": uri,
        "state": state,
        "scope": "profile openid email",
    }
    url = f"https://access.line.me/oauth2/v2.1/authorize?{urlencode(params)}"
    return {"url": url, "state": state}


@router.get("/line/callback", response_model=TokenResponse)
async def line_callback(
    code: str = Query(...),
    state: str = Query(...),
    redirect_uri: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    """Handle LINE Login callback, exchange code for JWT"""
    uri = redirect_uri or settings.LINE_LOGIN_REDIRECT_URI
    if uri not in ALLOWED_REDIRECT_URIS:
        raise HTTPException(status_code=400, detail="Invalid redirect_uri")
    # Exchange code for LINE tokens
    line_tokens = await exchange_line_code(code, uri)
    if not line_tokens:
        raise HTTPException(status_code=400, detail="Failed to exchange LINE code")

    # Get LINE user profile
    profile = await get_line_profile(line_tokens["access_token"])
    if not profile:
        raise HTTPException(status_code=400, detail="Failed to get LINE profile")

    # Upsert user
    result = await db.execute(select(User).where(User.line_user_id == profile["userId"]))
    user = result.scalar_one_or_none()

    if not user:
        user = User(
            line_user_id=profile["userId"],
            name=profile.get("displayName", "User"),
            avatar=profile.get("pictureUrl"),
        )
        db.add(user)
    else:
        user.name = profile.get("displayName", user.name)
        user.avatar = profile.get("pictureUrl", user.avatar)

    await db.commit()
    await db.refresh(user)

    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)

    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_token_str: str,
    db: AsyncSession = Depends(get_db),
):
    """Refresh access token"""
    payload = decode_token(refresh_token_str)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    user_id = int(payload["sub"])
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found")

    return TokenResponse(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
    )
