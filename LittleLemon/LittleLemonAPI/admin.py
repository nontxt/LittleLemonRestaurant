from django.contrib import admin
from .models import Category, MenuItem, Order, OrderItem, Cart

admin.site.register((MenuItem, Category, Cart, OrderItem, Order))
