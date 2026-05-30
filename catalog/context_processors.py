from cart.models import CartItem

def cart_count(request):
    if request.session.session_key:
        count = CartItem.objects.filter(session_id=request.session.session_key).count()
    else:
        count = 0
    return {'cart_count': count}