import uuid
from django.db import models
from django.conf import settings
from pytils.translit import slugify
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db.models.signals import post_save
from django.dispatch import receiver
from decimal import Decimal
from django.core.validators import MinValueValidator


# TODO 1. Добавить валидацию для полей, например, для email или для числовых полей.
# TODO 2. Изменить id на UUIDField для всех моделей, чтобы обеспечить уникальность и безопасность идентификаторов при переходе на PostgreSQL.

class Categories(models.Model):
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

class Brands(models.Model):
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

class Products(models.Model):
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
    category = models.ForeignKey(Categories,
        on_delete=models.CASCADE,
        verbose_name= "Категория",
        related_name="products")
    brand = models.ForeignKey(Brands,
        on_delete=models.CASCADE,
        verbose_name="Бренд")
    description = models.TextField("Описание", blank=True)
    # image = models.ImageField("Изображение", upload_to="products/")
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    updated_at = models.DateTimeField("Дата обновления",auto_now=True)
    # Добавляем слаг. unique=True обязателен, чтобы ссылки не дублировались.
    slug = models.SlugField("Слаг", max_length=200, unique=True, null=True, blank=True, help_text="Заполняется автоматически!")

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
    product = models.ForeignKey(
        Products,
        on_delete=models.CASCADE, verbose_name="Продукт"
    )
    price = models.DecimalField("Цена",
        max_digits=19, decimal_places=4, validators=[MinValueValidator(Decimal('0.00'))])
    version = models.IntegerField("Версия изменений",default=1)
    sku = models.CharField("Артикул", unique=True, blank=True, help_text="Уникальный идентификатор варианта товара. Заполняется автоматически при сохранении.")
    created_at = models.DateTimeField("Дата создания",
        auto_now_add=True)
    updated_at = models.DateTimeField("Дата обновления",
        auto_now=True)
    
    @property
    def name(self):
        # Поле ForeignKey называется product, поэтому обращаемся к нему
        return self.product.name

    @property
    def main_image_url(self):
        # Ищем первую попавшуюся картинку для этого товара
        first_image = self.product.product_images_set.first()
        if first_image and first_image.image:
            return first_image.image.url
        # Если картинок нет, возвращаем путь к заглушке
        return None 
    
    def __str__(self):
        # Выводим артикул
        return str(self.sku)
    
    def save(self, *args, **kwargs):
        if not self.sku:
            

            unique_hash = uuid.uuid4().hex[:8].upper()  # Генерируем уникальную часть для артикула
            self.sku = f"PRD-{self.product.id}-{unique_hash}"

        # Сохраняем за один SQL-запрос
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = "Вариант продукта"
        verbose_name_plural = "Варианты продуктов"
# В идеале добавить вес, размеры для расчёта доставки.

class CategoryAttributes(models.Model):
    id = models.AutoField(primary_key=True)
    category = models.ForeignKey(
        Categories,
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
    product = models.ForeignKey(
        Products,
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

class Carts(models.Model):
    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
# 1. Для авторизованных пользователей
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, # Ссылка на встроенную модель User
        on_delete=models.CASCADE,
        null=True,  # Может быть пустым, если это гость
        blank=True,
        related_name='cart'
    )
    # 2. Для анонимных гостей
    session_key = models.CharField("Ключ сессии", max_length=40, null=True, blank=True)

    def __str__(self):
        if self.user:
            return f"Корзина юзера {self.user.username}"
        return f"Анонимная корзина {self.session_key}"
    class Meta:
        verbose_name = "Корзина"
        verbose_name_plural = "Корзины"

class CartItems(models.Model):
    id = models.AutoField(primary_key=True)
    cart = models.ForeignKey(
        Carts,
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
# ---------------------------------- AUTH & IDENTITY MODELS ----------------------------------
class CustomUserManagers(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email обязателен!')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        # set_password автоматически создает password_hash и сохраняет его в поле password
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')
        return self.create_user(email, password, **extra_fields)

class Users(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        ('buyer', 'Покупатель'),
        ('seller', 'Продавец'),
        ('admin', 'Админ'),
    )
    
    id = models.AutoField(primary_key=True, editable=False)
    email = models.EmailField("Email", unique=True)
    role = models.CharField("Роль", max_length=20, choices=ROLE_CHOICES, default='buyer')
    is_active = models.BooleanField("Активен", default=True)
    is_staff = models.BooleanField("Доступ в админку", default=False)
    phone_number = models.CharField("Телефон", max_length=20, null=True, blank=True)

    objects = CustomUserManagers()

    USERNAME_FIELD = 'email' # Логинимся по email
    REQUIRED_FIELDS = []     # Дополнительных обязательных полей при создании нет

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

class UserProfiles(models.Model):
    # primary_key=True делает так, как на схеме: id профиля = id юзера
    user = models.OneToOneField(Users, on_delete=models.CASCADE, primary_key=True, related_name='profile')
    first_name = models.CharField("Имя", max_length=50, null=True, blank=True)
    last_name = models.CharField("Фамилия", max_length=50, null=True, blank=True)
    birth_date = models.DateField("Дата рождения", null=True, blank=True)
    avatar = models.ImageField("Аватар", upload_to='avatars/', null=True, blank=True)
    # preferences = models.JSONField("Настройки", default=dict, blank=True) 
    # TODO: сделать при переходе на PostgreSQL
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    class Meta:
        verbose_name = "Профиль пользователя"
        verbose_name_plural = "Профили пользователей"

class Addresses(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='addresses')
    country = models.CharField("Страна", max_length=100, null=True, blank=True)
    city = models.CharField("Город", max_length=100, null=True, blank=True)
    street = models.CharField("Улица", max_length=255, null=True, blank=True)
    zip_code = models.CharField("Индекс", max_length=20, null=True, blank=True)
    is_default = models.BooleanField("Основной адрес", default=False)
    
    # ВАЖНО ПО PostGIS:
    # На схеме есть поле location_geo со специфическим типом PostGIS(я думаю аддон поставим).
    # Пока мы сидим на SQLite (db.sqlite3), это поле работать не будет. 
    # Я его закомментировал. Когда перейдем на PostgreSQL, раскомментируем.
    # location_geo = django.contrib.gis.db.models.PointField(geography=True, srid=4326, null=True, blank=True) 
    # TODO: раскомментировать при переходе на PostgreSQL и установить PostGIS аддон для геолокации.
    class Meta:
        verbose_name = "Адрес"
        verbose_name_plural = "Адреса"
class StoreProfiles(models.Model):
    # PK и FK одновременно: жесткая привязка к пользователю 1:1
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        primary_key=True, 
        related_name='store_profile',
        verbose_name="Пользователь (Продавец)"
    )
    
    company_name = models.CharField("Название компании", max_length=255) # NN (Not Null)
    description = models.TextField("Описание", null=True, blank=True)
    logo = models.ImageField("Логотип", upload_to='store_logos/', null=True, blank=True)
    
    # max_digits=3, decimal_places=2 позволяет хранить значения от 0.00 до 9.99
    # rating = models.DecimalField("Рейтинг", max_digits=3, decimal_places=2, default=0.00) 
    # Отзывы и рейтинг не делаем, но если захотим база будет
    
    address = models.TextField("Юридический адрес", null=True, blank=True)
    is_verified = models.BooleanField("Верифицирован", default=False)
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)

    class Meta:
        verbose_name = "Профиль магазина"
        verbose_name_plural = "Профили магазинов"

    def __str__(self):
        return self.company_name
    
# Сигнал для автоматического создания профилей при регистрации нового пользователя
@receiver(post_save, sender=Users)
def create_user_profiles(sender, instance, created, **kwargs):
    if created:
        # Обычный профиль (UserProfile) создаем для ВСЕХ
        UserProfiles.objects.create(user=instance)
            
        # А профиль магазина (StoreProfile) — 
    if instance.role == 'seller':
        StoreProfiles.objects.create(
                user=instance, 
                company_name=f"Магазин пользователя {instance.email}"
            )    

# ---------------------------------- ORDER MANAGEMENT SYSTEM MODELS ----------------------------------

class Orders(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='orders'
    )

    STATUS_CHOICES = (
        ('pending', 'Ожидает оплаты'),
        ('paid', 'Оплачен'),
        ('shipped', 'Отправлен'),
        ('completed', 'Завершен'),
        ('cancelled', 'Отменен')
    )
    session_key = models.CharField("Ключ сессии", max_length=40, null=True, blank=True)
    created_at = models.DateTimeField("Дата создания",
        auto_now_add=True)
    updated_at = models.DateTimeField("Дата обновления",
        auto_now=True)
    status = models.CharField("Статус", max_length=20, choices=STATUS_CHOICES, default='pending')
    total_amount = models.DecimalField("Общая сумма", max_digits=19, decimal_places=4, default=0.00, validators=[MinValueValidator(Decimal('0.00'))])
    version = models.IntegerField("Версия изменений", default=1)
    cancellation_reason = models.TextField("Причина отмены", null=True, blank=True)
    # delivery_address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True) 
    # Адрес доставки, можно расширить до отдельной модели OrderAddress для хранения истории изменений адресов в заказе.

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"


class OrderItems(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    
    order = models.ForeignKey(
        'Order', # Ссылка на твою модель Order
        on_delete=models.CASCADE, 
        related_name='items'
    )
    
    # ВАЖНО: on_delete=models.SET_NULL. 
    # Если продавец удалит товар из базы, в истории заказов он останется (просто без ссылки).
    product_variant = models.ForeignKey(
        'Product_variant', 
        on_delete=models.SET_NULL, 
        null=True,
        verbose_name="Вариант товара"
    )
    
    # Прямая ссылка на продавца облегчает расчет выплат (не надо делать сложные JOIN'ы)
    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='sold_items',
        verbose_name="Продавец"
    )
    
    quantity = models.PositiveIntegerField("Количество", default=1)
    
    # Snapshot: Цена фиксируется в момент оформления заказа
    price_per_unit = models.DecimalField("Цена за штуку", max_digits=19, decimal_places=4, validators=[MinValueValidator(Decimal('0.00'))])
    
    # Вычисляемое поле. Ставим blank=True, так как будем считать его автоматически
    total_price = models.DecimalField("Итоговая цена", max_digits=19, decimal_places=4, blank=True, validators=[MinValueValidator(Decimal('0.00'))])

    def save(self, *args, **kwargs):
        # Реализуем формулу со схемы: (quantity * price_per_unit) 
        # Decimal нужен, чтобы не было багов с копейками при умножении
        if self.price_per_unit is not None and self.quantity is not None:
            raw_total = (Decimal(str(self.quantity)) * self.price_per_unit)

            self.total_price = max(raw_total, Decimal('0.0000'))
            
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Товар в заказе"
        verbose_name_plural = "Товары в заказах"

    def __str__(self):
        return f"Order {self.order.id} | Товар ID: {self.product_variant} (x{self.quantity})"
    
class Transactions(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    STATUS_CHOICES = (
        ('pending', 'Ожидает обработки'),
        ('completed', 'Завершена'),
        ('failed', 'Неудачная'),
        ('refunded', 'Возвращена'),
    )
    order = models.ForeignKey(Orders, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField("Сумма транзакции", max_digits=19, decimal_places=4, validators=[MinValueValidator(Decimal('0.00'))])
    transaction_id = models.CharField("ID транзакции", max_length=255, unique=True)
    payment_method = models.CharField("Метод оплаты", max_length=50)
    status = models.CharField("Статус транзакции", max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)

    class Meta:
        verbose_name = "Транзакция"
        verbose_name_plural = "Транзакции"


class Warehouses(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    name = models.CharField("Название склада", max_length=255)
    store = models.ForeignKey(
    StoreProfiles, on_delete=models.CASCADE, related_name='warehouses', verbose_name="Продавец (Магазин)")
    address = models.TextField("Адрес склада")
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    is_active = models.BooleanField("Активный", default=True) # Для логической деактивации склада без удаления из базы
    # country = models.CharField("Страна", max_length=100, null=True, blank=True)
    # city = models.CharField("Город", max_length=100, null=True, blank=True)
    # TODO: добавить геолокацию для оптимизации логистики при переходе на PostgreSQL и PostGIS (например, поле location_geo = PointField)
    # TODO: решить вопрос необходимости полей city и country, если есть поле address. Возможно, стоит их добавить для удобства фильтрации и оптимизации логистики.

    class Meta:
        verbose_name = "Склад"
        verbose_name_plural = "Склады"


class Stocks(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    product_variant = models.ForeignKey(Product_variants, on_delete=models.CASCADE, related_name='stock')
    warehouse = models.ForeignKey(Warehouses, on_delete=models.CASCADE, related_name='stock')
    quantity = models.PositiveIntegerField("Количество на складе", default=0)
    reserved_quantity = models.PositiveIntegerField("Зарезервированное количество", default=0) # Кол-во, зарезервированное в заказах, но еще не списанное

    class Meta:
        verbose_name = "Остаток на складе"
        verbose_name_plural = "Остатки на складах"
        unique_together = ('product_variant', 'warehouse')


class Messages(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_messages',
        verbose_name="Отправитель"
    )
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='received_messages',
        verbose_name="Получатель"
    )
    content = models.TextField("Содержание сообщения")
    created_at = models.DateTimeField("Дата отправки", auto_now_add=True)
    is_read = models.BooleanField("Прочитано", default=False)

    class Meta:
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"

    def __str__(self):
        return f"Сообщение от {self.sender.email} к {self.recipient.email}"
    