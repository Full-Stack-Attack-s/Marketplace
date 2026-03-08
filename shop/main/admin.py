from django.contrib import admin
from .models import *


from django.contrib import admin
from .models import (
    Category, Brand, Product, Product_variants, 
    Category_id, Product_images, Cart, CartItem
)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'id', 'slug', 'path')
    search_fields = ('name', 'slug')
    # Магия автозаполнения слага из названия
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ('parent',)

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'id', 'slug')
    search_fields = ('name',)
    # Магия автозаполнения слага из названия
    prepopulated_fields = {'slug': ('name',)}

# === INLINES (Встроенные блоки для Товара) ===
class ProductVariantInline(admin.TabularInline):
    model = Product_variants
    extra = 1  # Сколько пустых строк для добавления вариантов показывать сразу
    fields = ('sku', 'price', 'version')

class ProductImageInline(admin.TabularInline):
    model = Product_images
    extra = 1
    fields = ('image', 'is_main', 'sort_order')

# === АДМИНКА ТОВАРА ===
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category_id', 'id', 'brand_id', 'status', 'created_at', 'status')
    list_filter = ('status', 'category_id', 'brand_id')
    search_fields = ('name', 'description')
    # Подключаем встроенные блоки фото и цен
    inlines = [ProductVariantInline, ProductImageInline]

@admin.register(Category_id)
class CategoryAttributeAdmin(admin.ModelAdmin):
    list_display = ('id', 'category_id', 'key', 'label', 'type', 'is_required')
    list_filter = ('category_id', 'type')

# === INLINES (Встроенные блоки для Корзины) ===
class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_id', 'session_key', 'created_at', 'updated_at')
    inlines = [CartItemInline]

# Отдельная регистрация вариантов и картинок (если захочешь искать их вне товара)
@admin.register(Product_variants)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ('id', 'product_id', 'sku', 'price', 'updated_at')
    search_fields = ('sku',)

@admin.register(Product_images)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'product_id', 'is_main', 'sort_order')


# Register your models here.
