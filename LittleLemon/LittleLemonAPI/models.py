from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    slug = models.SlugField()
    title = models.CharField(db_index=True, max_length=255)

    def __str__(self):
        return self.title


class MenuItem(models.Model):
    title = models.CharField(db_index=True, max_length=255)
    price = models.DecimalField(db_index=True, max_digits=6, decimal_places=2)
    featured = models.BooleanField(db_index=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)

    def __str__(self):
        return self.title


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    menuitem = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.SmallIntegerField()

    # This is extra fields
    # unit_price = models.DecimalField(max_digits=6, decimal_places=2)
    # price = models.DecimalField(max_digits=6, decimal_places=2)

    class Meta:
        unique_together = ('menuitem', 'user')


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    delivery_crew = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='delivery_crew', null=True)
    status = models.BooleanField(db_index=True, default=0)
    total = models.DecimalField(max_digits=6, decimal_places=2)
    date = models.DateField(db_index=True, auto_now=True)

    def __str__(self):
        return f'Order № {self.pk} - {self.user}'


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    menuitem = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.SmallIntegerField()
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)
    price = models.DecimalField(max_digits=6, decimal_places=2)

    class Meta:
        unique_together = ('order', 'menuitem')

    def __str__(self):
        return f'Order № {self.order.id} - {self.menuitem.title}'
