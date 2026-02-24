from django.shortcuts import render
from django.shortcuts import render, redirect
from .forms import RegisterForm
from django.contrib.auth import login
from django.http import HttpResponse


def index(request):
    return render(request,"index.html")
def cart(request):
    return render(request, "cart.html")
def profile(request):
    return render(request, "profile.html")
def forms(request):
    return render(request, "forms.html")