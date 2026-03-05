from django.contrib import admin
from .models import *


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'created_at')
    # Магия автозаполнения слага из названия
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'slug')
    # Магия автозаполнения слага из названия
    prepopulated_fields = {'slug': ('name',)}

    def get_full_slug(self):
        """Собирает путь вида 'electronics/smartphones/apple'"""
        full_path = [self.slug]
        k = self.parent
        while k is not None:
            full_path.append(k.slug)
            k = k.parent
        return '/'.join(full_path[::-1])


# Register your models here.
