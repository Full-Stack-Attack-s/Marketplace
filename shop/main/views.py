from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
def index(request):
    return render(request,"index.html")
def cart(request):
    return render(request, "cart.html")
def profile(request):
    return render(request, "profile.html")