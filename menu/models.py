from django.db import models

# Create your models here.
class Menu(models.Model):
    name = models.CharField(max_length=255, default='')
    ingredients = models.CharField(max_length=255, null=True)
    category = models.CharField(max_length=255, default='Egyéb')
    price = models.CharField(max_length=255, default='0')

    def __str__(self):
        return f"{self.name} ({self.category})"