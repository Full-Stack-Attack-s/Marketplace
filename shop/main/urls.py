from django.urls import path, include

from . import views
from . import  models

urlpatterns = [
    path("", views.index, name="index"),
    path("cart/", views.cart, name="cart"),
    path("profile/", views.profile, name="profile"),
    path("cards/", views.cards, name="cards"),
    path("catalog/", views.catalog, name="catalog"),
    path('accounts/', include('allauth.urls')),
    path('get-attributes/<int:category_id>/', views.get_attributes, name='get_attributes'),
    path('quick-update/<int:product_id>/', views.quick_update_product, name='quick_update_product'),
    path('seller/products/', views.manage_products, name='manage_products'),
    path('seller/products/edit/<int:product_id>/', views.edit_product, name='edit_product'),
    path('seller/dashboard/', views.seller_dashboard, name='seller_dashboard'),
    path('seller/profile/', views.seller_profile, name='seller_profile'),
    path('seller/products/add/', views.add_product, name='add_product'),
    path('api/category-attributes/<int:category_id>/', views.get_category_attributes, name='get_category_attributes'),
]

    #path('category/<path:category_path>/', views.category_detail)
    # path("products/<int:product_id>/", views., name = "detail")
