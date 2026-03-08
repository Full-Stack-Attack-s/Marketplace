from django.db import models
from django.conf import settings
from pytils.translit import slugify
from django.core.exceptions import ValidationError

class Category(models.Model):
    name = models.CharField("Название", max_length=100)
    id = models.AutoField(primary_key=True)
    path = models.CharField(verbose_name="Путь", max_length=255, db_index=True, unique=True, null=True, blank=True, help_text="Заполняется автоматически!")
    # parent ссылается на эту же таблицу ('self')
    parent = models.ForeignKey(verbose_name="Родительская категория", to='self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    slug = models.SlugField("Слаг", unique=True,  help_text="Заполняется автоматически!")


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

class Brand(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.TextField("Название", max_length=100)
    slug = models.TextField("Слаг",unique=True, null=True, blank=True)
    logo_image = models.ImageField("Лого", upload_to="brands/")

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        if is_new:
            super().save(*args, **kwargs) # Сохраняем, чтобы БД выдала ID
            
        # Генерируем слаг с транслитом и ID
        base_slug = slugify(self.name)
        suffix = f"-{self.id}"
        
        if not str(self.slug).endswith(suffix):
            self.slug = f"{base_slug}{suffix}"
            super().save(update_fields=['slug']) # Перезаписываем только слаг

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Бренд"
        verbose_name_plural = "Бренды"

class Product(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Черновик'),
        ('active', 'Активен'),
        ('archived', 'В архиве'),
    )
    status = models.CharField("Статус", max_length=20, help_text="Управляет видимостью товара на сайте. " \
    "Черновик(draft) - не показывается, Активен(active) - показывается, " \
    "В архиве(archived) - не показывается и не участвует в поиске.", 
    choices=STATUS_CHOICES, default='draft')

    # Связь "Многие к одному": у одной категории может быть много товаров
    id = models.AutoField(primary_key=True)
    name = models.CharField("Название", max_length=200)
    category_id = models.ForeignKey(Category,
        on_delete=models.CASCADE,
        verbose_name= "Категория",
        related_name="products")
    brand_id = models.ForeignKey(Brand,
        on_delete=models.CASCADE,
        verbose_name="Бренд")
    description = models.TextField("Описание", blank=True)
    # image = models.ImageField("Изображение", upload_to="products/")
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    updated_at = models.DateTimeField("Дата обновления",auto_now=True)
    # Добавляем слаг. unique=True обязателен, чтобы ссылки не дублировались.
    slug = models.SlugField("Слаг", max_length=200, unique=True, null=True, blank=True)

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        if is_new:
            super().save(*args, **kwargs) # Сохраняем, чтобы БД выдала ID
            
        # Генерируем слаг с транслитом и ID
        base_slug = slugify(self.name)
        suffix = f"-{self.id}"
        
        if not str(self.slug).endswith(suffix):
            self.slug = f"{base_slug}{suffix}"
            super().save(update_fields=['slug']) # Перезаписываем только слаг

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Продукт"
        verbose_name_plural = "Продукты"

class Product_variants(models.Model):
    id = models.AutoField(primary_key=True)
    product_id = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
    )
    price = models.DecimalField("Цена",
        max_digits=10, decimal_places=4)
    version = models.IntegerField("Версия изменений",default=1)
    sku = models.TextField("Артикул", unique=True, blank=True)
    created_at = models.DateTimeField("Дата создания",
        auto_now_add=True)
    updated_at = models.DateTimeField("Дата обновления",
        auto_now=True)
    
    @property
    def name(self):
        # Поле ForeignKey называется product_id, поэтому обращаемся к нему
        return self.product_id.name

    @property
    def main_image_url(self):
        # Ищем первую попавшуюся картинку для этого товара
        first_image = self.product_id.product_images_set.first()
        if first_image and first_image.image:
            return first_image.image.url
        # Если картинок нет, возвращаем путь к заглушке
        return None 
    
    def __str__(self):
        # Выводим артикул
        return str(self.sku)
    
    class Meta:
        verbose_name = "Вариант продукта"
        verbose_name_plural = "Варианты продуктов"
# В идеале добавить вес, размеры для расчёта доставки.

class Category_id(models.Model):
    id = models.AutoField(primary_key=True)
    category_id = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        verbose_name="Категория",
    )
    key = models.TextField(help_text="Например: ram_capacity") # Надо пропиасть not null
    label = models.TextField("Название",
        help_text= "Например: Объем оперативной памяти ")
    type = models.TextField("Тип", help_text= "Например: text, number, boolean, select ")
    # options = models.JSONField(verbose_name= "Опции")
    # нужно при type = select.
    # Например: ["8 ГБ", "16 ГБ", "32 ГБ"].
    # Сделать при переходе на PostgreSQL
    is_required = models.BooleanField(default=False)
    is_filterable = models.BooleanField(default=False)

    
    def __str__(self):
        return str(self.label)
    
    class Meta:
        verbose_name = "Атрибут категории"
        verbose_name_plural = "Атрибуты категорий"

class Product_images(models.Model):
    id = models.AutoField(primary_key=True)
    product_id = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
    )
    image = models.ImageField(upload_to="products/")
    sort_order = models.IntegerField(default=1)
    is_main = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Фото {self.id}"
    
    class Meta:
        verbose_name = "Изображение продукта"
        verbose_name_plural = "Изображения продуктов"

class Cart(models.Model):
    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
# 1. Для авторизованных пользователей
    user_id = models.ForeignKey(
        settings.AUTH_USER_MODEL, # Ссылка на встроенную модель User
        on_delete=models.CASCADE,
        null=True,  # Может быть пустым, если это гость
        blank=True,
        related_name='cart'
    )
    # 2. Для анонимных гостей
    session_key = models.CharField(max_length=40, null=True, blank=True)

    def __str__(self):
        if self.user:
            return f"Корзина юзера {self.user.username}"
        return f"Анонимная корзина {self.session_key}"
    class Meta:
        verbose_name = "Корзина"
        verbose_name_plural = "Корзины"

class CartItem(models.Model):
    id = models.AutoField(primary_key=True)
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items'
    )
    product_variant = models.ForeignKey(
        Product_variants,
        on_delete=models.CASCADE
    )
    quantity = models.PositiveIntegerField(default=1, verbose_name="Количество")
    
    def __str__(self):
        return f"Позиция корзины: {self.id}"
    
    class Meta:
        verbose_name = "Товар в корзине"
        verbose_name_plural = "Товары в корзинах"

class Order(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='orders'
    )
    session_key = models.CharField(max_length=40, null=True, blank=True)
    created_at = models.DateTimeField("Дата создания",
         auto_now_add=True)