from django.contrib import admin
from .models import *

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
    model = Product_variant
    extra = 1  # Сколько пустых строк для добавления вариантов показывать сразу
    fields = ('sku', 'price', 'version')

class ProductImageInline(admin.TabularInline):
    model = Product_image
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

@admin.register(CategoryAttribute)
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

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'cart_id', 'product_variant_id', 'quantity')
    search_fields = ('cart__user__email', 'product_variant__sku')

# Отдельная регистрация вариантов и картинок (если захочешь искать их вне товара)
@admin.register(Product_variant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ('id', 'product_id', 'sku', 'price', 'updated_at')
    search_fields = ('sku',)

@admin.register(Product_image)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'product_id', 'is_main', 'sort_order')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_id', 'session_key', 'created_at', 'updated_at')

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'order_id', 'product_variant_id', 'quantity', 'total_price')

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'is_staff', 'is_active', 'role', 'phone_number')
    search_fields = ('email', 'first_name', 'last_name')

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'first_name', 'last_name', )
    search_fields = ('user_id__email', 'phone_number')

@admin.register(StoreProfile)
class StoreProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'company_name', 'is_verified', 'created_at')
    search_fields = ('company_name', 'user__email')
    list_filter = ('is_verified', 'created_at')

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'street', 'city', 'zip_code', 'country')
    search_fields = ('street', 'city', 'zip_code')

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'amount', 'status', 'created_at')
    search_fields = ('user__email', 'amount')

@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'address')
    search_fields = ('name', 'address')

@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ('id', 'product_variant_id', 'warehouse_id', 'quantity', 'reserved_quantity')
    search_fields = ('product_variant__sku', 'warehouse__name')
    list_filter = ('warehouse', 'product_variant__product__category')

# Register your models here.
