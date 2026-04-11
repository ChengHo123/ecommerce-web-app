def cart_count(request):
    if request.user.is_authenticated:
        try:
            return {"cart_count": request.user.cart.item_count}
        except Exception:
            pass
    return {"cart_count": 0}
