from django.db import models


class Product(models.Model):
    name = models.CharField("Название", max_length=200)
    price = models.IntegerField("Цена")
    description = models.TextField("Описание", blank=True)
    image = models.ImageField("Изображение", upload_to="products/")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


from django.db import models

# Create your models here.
