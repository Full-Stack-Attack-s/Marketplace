from .models import Favorites

def favorites_context(request):
    if request.user.is_authenticated:
        # Получаем ID всех избранных товаров пользователя
        user_favorites = Favorites.objects.filter(user=request.user).values_list('product_id', flat=True)
        return {'user_favorites': list(user_favorites), 'favorites_count': user_favorites.count()}
    return {'user_favorites': [], 'favorites_count': 0}

def cart_context(request):
    from .models import Carts
    # Пытаемся найти корзину по сессии или пользователю
    cart = None
    if request.user.is_authenticated:
        cart = Carts.objects.filter(user=request.user).first()
    else:
        session_key = request.session.session_key
        if session_key:
            cart = Carts.objects.filter(session_key=session_key).first()
    
    count = 0
    if cart:
        count = cart.items.count()
        
    return {'cart_count_global': count}