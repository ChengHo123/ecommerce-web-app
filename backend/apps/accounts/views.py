import logging
import secrets
from urllib.parse import urlencode
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib import messages
from django.conf import settings
from apps.accounts.models import User
from services.line_auth import exchange_line_code, get_line_profile

logger = logging.getLogger("apps.accounts")


def login_view(request):
    if request.user.is_authenticated:
        return redirect("/")
    return render(request, "auth/login.html")


def line_login_redirect(request):
    state = secrets.token_urlsafe(16)
    request.session["line_oauth_state"] = state
    params = {
        "response_type": "code",
        "client_id": settings.LINE_LOGIN_CHANNEL_ID,
        "redirect_uri": settings.LINE_LOGIN_REDIRECT_URI,
        "state": state,
        "scope": "profile openid email",
    }
    url = f"https://access.line.me/oauth2/v2.1/authorize?{urlencode(params)}"
    return redirect(url)


def line_callback(request):
    code = request.GET.get("code")
    state = request.GET.get("state")

    if not code or state != request.session.get("line_oauth_state"):
        logger.warning("LINE callback state mismatch: ip=%s code_present=%s",
                       request.META.get("REMOTE_ADDR"), bool(code))
        messages.error(request, "LINE 登入失敗，請重試。")
        return redirect("/auth/login/")

    line_tokens = exchange_line_code(code, settings.LINE_LOGIN_REDIRECT_URI)
    if not line_tokens:
        logger.error("LINE token exchange failed: ip=%s", request.META.get("REMOTE_ADDR"))
        messages.error(request, "無法取得 LINE Token。")
        return redirect("/auth/login/")

    profile = get_line_profile(line_tokens["access_token"])
    if not profile:
        logger.error("LINE profile fetch failed")
        messages.error(request, "無法取得 LINE 個人資料。")
        return redirect("/auth/login/")

    user, created = User.objects.get_or_create(
        line_user_id=profile["userId"],
        defaults={
            "name": profile.get("displayName", "User"),
            "avatar": profile.get("pictureUrl", ""),
        },
    )
    if not created:
        user.name = profile.get("displayName", user.name)
        user.avatar = profile.get("pictureUrl", user.avatar) or user.avatar
        user.save(update_fields=["name", "avatar"])

    login(request, user, backend="django.contrib.auth.backends.ModelBackend")
    logger.info("LINE login: user=%s (pk=%d) new=%s ip=%s",
                user.name, user.pk, created, request.META.get("REMOTE_ADDR"))
    next_url = request.session.pop("next", "/")
    return redirect(next_url)


def logout_view(request):
    logout(request)
    return redirect("/")
