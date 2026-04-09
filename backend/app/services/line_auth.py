import httpx
from app.core.config import settings


async def exchange_line_code(code: str, redirect_uri: str | None = None) -> dict | None:
    """Exchange LINE authorization code for tokens"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.line.me/oauth2/v2.1/token",
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": redirect_uri or settings.LINE_LOGIN_REDIRECT_URI,
                "client_id": settings.LINE_LOGIN_CHANNEL_ID,
                "client_secret": settings.LINE_LOGIN_CHANNEL_SECRET,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        if response.status_code == 200:
            return response.json()
        return None


async def get_line_profile(access_token: str) -> dict | None:
    """Get LINE user profile using access token"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://api.line.me/v2/profile",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        if response.status_code == 200:
            return response.json()
        return None
