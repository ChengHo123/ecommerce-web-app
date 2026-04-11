import httpx
from django.conf import settings


def exchange_line_code(code: str, redirect_uri: str) -> dict | None:
    try:
        resp = httpx.post(
            "https://api.line.me/oauth2/v2.1/token",
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": redirect_uri,
                "client_id": settings.LINE_LOGIN_CHANNEL_ID,
                "client_secret": settings.LINE_LOGIN_CHANNEL_SECRET,
            },
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()
    except Exception:
        return None


def get_line_profile(access_token: str) -> dict | None:
    try:
        resp = httpx.get(
            "https://api.line.me/v2/profile",
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()
    except Exception:
        return None
