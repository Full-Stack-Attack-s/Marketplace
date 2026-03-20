from django.http import HttpResponse
from django.shortcuts import render
from django.db.models import Sum, F, IntegerField
from django.db.models.functions import Coalesce
from .models import models
from .models import Products

# def index(request):
    ## Достаем варианты и сразу "приклеиваем" к ним родительский товар
    ## Ограничим до 20 штук для главной страницы
    # variants = models.Product_variants.objects.select_related('product_id').all()[:20]
    
    ## Отправляем в шаблон под тем именем, которое ты используешь в цикле
    # return render(request, "index.html", {"products_variants": variants})

def index(request):
    #Cчитаем реальные остатки прямо внутри SQL-запроса
    popular_products = Products.objects.filter(status='active').annotate(
        # Суммируем количество со всех складов для всех вариантов товара. 
        # Coalesce нужен, чтобы заменить NULL на 0, если складов еще нет.
        total_quantity=Coalesce(Sum('product_variants__stock__quantity'), 0, output_field=IntegerField()),
        total_reserved=Coalesce(Sum('product_variants__stock__reserved_quantity'), 0, output_field=IntegerField())
    ).annotate(
        # Считаем свободный остаток: всё, что на складе МИНУС то, что уже в чужих заказах
        available_stock=F('total_quantity') - F('total_reserved')
    ).filter(
        # ЖЕСТКИЙ ФИЛЬТР: выводим на витрину только те товары, где есть хотя бы 1 свободная штука
        available_stock__gt=0 
    ).order_by('-sales_count')[:10]

    return render(request, 'index.html', {'products': popular_products})

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

    return render(request, "catalog.html")

