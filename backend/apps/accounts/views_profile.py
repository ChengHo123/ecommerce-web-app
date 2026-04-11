from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages


@login_required
def profile_view(request):
    user = request.user
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        phone = request.POST.get("phone", "").strip()
        if name:
            user.name = name
            user.phone = phone or None
            user.save(update_fields=["name", "phone"])
            messages.success(request, "個人資料已更新。")
        return redirect("/profile/")
    return render(request, "auth/profile.html", {"user": user})
