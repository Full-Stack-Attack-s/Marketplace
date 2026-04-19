from .models import Favorites

def favorites_context(request):
    if request.user.is_authenticated:
        # Получаем ID всех избранных товаров пользователя
        user_favorites = Favorites.objects.filter(user=request.user).values_list('product_id', flat=True)
        return {'user_favorites': list(user_favorites)}
    return {'user_favorites': []}