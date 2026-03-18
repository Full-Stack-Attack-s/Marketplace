from django.urls import path

from . import views
from . import  models

urlpatterns = [
    path("", views.index, name="index"),
    path("cart/", views.cart, name="cart"),
    path("profile/", views.profile, name="profile"),
    path("cards/", views.cards, name="cards"),
    path("catalog/", views.catalog, name="catalog"),
    #path('category/<path:category_path>/', views.category_detail)
    # path("products/<int:product_id>/", views., name = "detail")
]