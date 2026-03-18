from django.http import HttpResponse
from django.shortcuts import render
from . import models

def index(request):
    # Достаем варианты и сразу "приклеиваем" к ним родительский товар
    # Ограничим до 20 штук для главной страницы
    variants = models.Product_variants.objects.select_related('product_id').all()[:20]
    
    # Отправляем в шаблон под тем именем, которое ты используешь в цикле
    return render(request, "index.html", {"products_variant": variants})

def cart(request):
    return render(request, "cart.html")
def profile(request):
    return render(request, "profile.html")
def cards(request):
    return render(request, "cards.html")
def catalog(request):
    return render(request, "catalog.html")

def checkout_view(request):
    # 1. Если сессии еще нет (гость ничего не делал на сайте), Джанго должен её физически создать
    if not request.session.session_key:
        request.session.create()

    # 2. Забираем сгенерированный ключ (например, '5b3v2xjf...')
    current_session_key = request.session.session_key

    # 3. Создаем заказ и подставляем ключ в поле session_key
    order = models.Orders.objects.create(
        session_key=current_session_key,
        
        # Сразу умная проверка: если юзер авторизован, пишем его объект в user_id. 
        # Если нет (аноним) — пишем None (это разрешено твоим null=True)
        user_id=request.user if request.user.is_authenticated else None
    )
    
    # ... дальше логика добавления конкретных товаров в этот заказ ...