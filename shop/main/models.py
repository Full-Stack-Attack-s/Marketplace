from django.db import models

class Category(models.Model):
    name = models.CharField("Название", max_length=100)
    # parent ссылается на эту же таблицу ('self')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subcategories')
    slug = models.SlugField("Слаг", unique=True, help_text="Например: smartphones")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

class Product(models.Model):
    # Связь "Многие к одному": у одной категории может быть много товаров
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        verbose_name="Категория",
        related_name="products"  # Позволяет найти товары через категорию: category.products.all()
    )
    name = models.CharField("Название", max_length=200)
    price = models.IntegerField("Цена")
    description = models.TextField("Описание", blank=True)
    image = models.ImageField("Изображение", upload_to="products/")
    created_at = models.DateTimeField(auto_now_add=True)
    # Добавляем слаг. unique=True обязателен, чтобы ссылки не дублировались.
    slug = models.SlugField("Слаг", max_length=200, unique=True, null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Продукт"
        verbose_name_plural = "Продукты"

from django.db import models

# Create your models here.
