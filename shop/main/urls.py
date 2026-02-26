from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("cart/", views.cart, name="cart"),
    path("profile/", views.profile, name="profile"),
    path("cards/", views.cards, name="cards"),
]