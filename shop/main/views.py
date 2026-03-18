from django.shortcuts import render
from . import models

# Create your views here.
from django.http import HttpResponse
def index(request):
    products=models.Product.objects.all()
    return render(request,"index.html", {"products":products})

def cart(request):
    return render(request, "cart.html")
def profile(request):
    return render(request, "profile.html")
def cards(request):
    return render(request, "cards.html")
def catalog(request):
    return render(request, "catalog.html")