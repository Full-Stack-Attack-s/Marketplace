from django.contrib import admin
from .models import *

@admin.register(Categories)
class CategoriesAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'id', 'slug', 'path')
    search_fields = ('name', 'slug')
    # Магия автозаполнения слага из названия
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ('parent',)

@admin.register(Brands)
class BrandsAdmin(admin.ModelAdmin):
    list_display = ('name', 'id', 'slug')
    search_fields = ('name',)
    # Магия автозаполнения слага из названия
    prepopulated_fields = {'slug': ('name',)}

# === INLINES (Встроенные блоки для Товара) ===
class ProductVariantsInline(admin.TabularInline):
    model = Product_variants
    extra = 1  # Сколько пустых строк для добавления вариантов показывать сразу
    fields = ('sku', 'price', 'version')

class ProductImagesInline(admin.TabularInline):
    model = Product_images
    extra = 1
    fields = ('image', 'is_main', 'sort_order')



# === АДМИНКА ТОВАРА ===
@admin.register(Products)
class ProductsAdmin(admin.ModelAdmin):
    list_display = ('name', 'category_id', 'id', 'brand_id', 'status', 'created_at', 'status')
    list_filter = ('status', 'category_id', 'brand_id')
    search_fields = ('name', 'description')
    # Подключаем встроенные блоки фото и цен
    inlines = [ProductVariantsInline, ProductImagesInline]

@admin.register(CategoryAttributes)
class CategoryAttributesAdmin(admin.ModelAdmin):
    list_display = ('id', 'category_id', 'key', 'label', 'type', 'is_required')
    list_filter = ('category_id', 'type')

# === INLINES (Встроенные блоки для Корзины) ===
class CartItemsInline(admin.TabularInline):
    model = CartItems
    extra = 0

@admin.register(Carts)
class CartsAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_id', 'session_key', 'created_at', 'updated_at')
    inlines = [CartItemsInline]

@admin.register(CartItems)
class CartItemsAdmin(admin.ModelAdmin):
    list_display = ('id', 'cart_id', 'product_variant_id', 'quantity')
    search_fields = ('cart__user__email', 'product_variant__sku')

# Отдельная регистрация вариантов и картинок (если захочешь искать их вне товара)
@admin.register(Product_variants)
class ProductVariantsAdmin(admin.ModelAdmin):
    list_display = ('name', 'product_id', 'sku', 'price', 'updated_at', 'id')
    search_fields = ('sku',)

@admin.register(Product_images)
class ProductImagesAdmin(admin.ModelAdmin):
    list_display = ('id', 'product_id', 'is_main', 'sort_order')


@admin.register(Orders)
class OrdersAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_id', 'session_key', 'created_at', 'updated_at')

@admin.register(OrderItems)
class OrderItemsAdmin(admin.ModelAdmin):
    list_display = ('id', 'order_id', 'product_variant_id', 'quantity', 'total_price')

@admin.register(Users)
class UsersAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'is_staff', 'is_active', 'role', 'phone_number')
    search_fields = ('email', 'first_name', 'last_name')

@admin.register(UserProfiles)
class UserProfilesAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'first_name', 'last_name', )
    search_fields = ('user_id__email', 'phone_number')

@admin.register(StoreProfiles)
class StoreProfilesAdmin(admin.ModelAdmin):
    list_display = ('user', 'company_name', 'is_verified', 'created_at')
    search_fields = ('company_name', 'user__email')
    list_filter = ('is_verified', 'created_at')

@admin.register(Addresses)
class AddressesAdmins(admin.ModelAdmin):
    list_display = ('id', 'user', 'street', 'city', 'zip_code', 'country')
    search_fields = ('street', 'city', 'zip_code')

@admin.register(Transactions)
class TransactionsAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'amount', 'status', 'created_at')
    search_fields = ('user__email', 'amount')

@admin.register(Warehouses)
class WarehousesAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'address')
    search_fields = ('name', 'address')

@admin.register(Stocks)
class StocksAdmin(admin.ModelAdmin):
    list_display = ('id', 'product_variant_id', 'warehouse_id', 'quantity', 'reserved_quantity')
    search_fields = ('product_variant__sku', 'warehouse__name')
    list_filter = ('warehouse', 'product_variant__product__category')

# Register your models here.
