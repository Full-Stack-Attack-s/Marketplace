from django.http import HttpResponse
from django.shortcuts import render
from . import models

def index(request):
    # Достаем варианты и сразу "приклеиваем" к ним родительский товар
    # Ограничим до 20 штук для главной страницы
    variants = models.Product_variants.objects.select_related('product_id').all()[:20]
    
    # Отправляем в шаблон под тем именем, которое ты используешь в цикле
    return render(request, "index.html", {"products_variants": variants})

def cart(request):
    return render(request, "cart.html")
def profile(request):
    return render(request, "profile.html")
def cards(request):
    return render(request, "cards.html")