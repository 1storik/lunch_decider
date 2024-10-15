from django.db import models
from django.contrib.auth.models import User
import uuid


class Restaurant(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    api_key = models.UUIDField(default=uuid.uuid4, unique=True, null=True)

    def __str__(self):
        return self.name


class Dish(models.Model):
    restaurant = models.ForeignKey(Restaurant, related_name='dishes', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)

    class Meta:
        unique_together = ('restaurant', 'name')

    def __str__(self):
        return f"{self.name} ({self.restaurant.name})"


class Menu(models.Model):
    restaurant = models.ForeignKey(Restaurant, related_name='menus', on_delete=models.CASCADE)
    date = models.DateField()
    name = models.CharField(max_length=50)
    dishes = models.ManyToManyField(Dish, related_name='menus')

    class Meta:
        unique_together = ('restaurant', 'date', 'name')

    def __str__(self):
        return f"{self.name} for {self.date} at {self.restaurant.name}"


class Vote(models.Model):
    user = models.ForeignKey(User, related_name='votes', on_delete=models.CASCADE)
    menu = models.ForeignKey(Menu, related_name='votes', on_delete=models.CASCADE)
    voted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'menu')

    def __str__(self):
        return f"{self.user.username} voted for {self.menu.restaurant.name} on {self.menu.date}"
