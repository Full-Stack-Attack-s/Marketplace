from django.db import models

class Category(models.Model):
    name = models.CharField("Название", max_length=100)
    id = models.AutoField(primary_key=True)
    path = models.CharField(verbose_name="Путь", max_length=255, db_index=True, unique=True, null=True, blank=True, help_text="Заполняется автоматически!")
    # parent ссылается на эту же таблицу ('self')
    parent = models.ForeignKey(verbose_name="Родительская категория", to='self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    slug = models.SlugField("Слаг", unique=True, help_text="Заполняется автоматически!")

    from django.core.exceptions import ValidationError

    def save(self, *args, **kwargs):
        # 1. Сначала сохраняем, чтобы получить ID (если объект новый)
        is_new = self.pk is None
        if is_new:
            super().save(*args, **kwargs)
        # 1.1. Теперь у нас точно есть ID. Формируем "хвост" для слага
        suffix = f"-{self.id}"
        if not str(self.slug).endswith(suffix):
            self.slug = f"{self.slug}{suffix}"

        # 2. Формируем путь, только если поле path уже существует в классе
        if self.parent:
            # Приклеиваем ID к пути родителя
            self.path = f"{self.parent.path}{self.id}/"
        else:
            # Если родителя нет — это корень
            self.path = f"{self.id}/"

        # 3. Финальное сохранение пути и слага
        # (Добавь сюда свою логику слага из прошлых шагов)
        super().save(*args, **kwargs)

    def __str__(self):
        # Если есть родитель, рекурсивно вызываем его имя + текущее
        if self.parent:
            return f"{self.parent}  >  {self.name}"
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
    id = models.AutoField(primary_key=True)
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
