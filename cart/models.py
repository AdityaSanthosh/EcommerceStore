from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Item(models.Model):
    name = models.CharField(max_length=30)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.DO_NOTHING)

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    description = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
