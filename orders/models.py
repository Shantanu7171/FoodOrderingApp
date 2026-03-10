from django.db import models
from accounts.models import User
from menu.models import Dish

class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    payment_id = models.CharField(max_length=100)
    payment_method = models.CharField(max_length=100)
    amount_paid = models.CharField(max_length=100)
    status = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.payment_id

class Order(models.Model):
    STATUS = (
        ('New', 'New'),
        ('Accepted', 'Accepted'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    )

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    payment = models.ForeignKey('Payment', on_delete=models.SET_NULL, blank=True, null=True)
    order_number = models.CharField(max_length=20, default='')
    first_name = models.CharField(max_length=50, default='')
    last_name = models.CharField(max_length=50, default='')
    phone = models.CharField(max_length=15, blank=True, default='')
    email = models.EmailField(max_length=50, default='')
    address = models.CharField(max_length=200, default='')
    country = models.CharField(max_length=15, blank=True, default='')
    state = models.CharField(max_length=15, blank=True, default='')
    city = models.CharField(max_length=50, default='')
    pin_code = models.CharField(max_length=10, default='')
    total = models.FloatField(default=0)
    tax_data = models.JSONField(blank=True, help_text="Data format: {'tax_type':{'tax_percentage': integer, 'tax_amount': decimal}}", null=True)
    total_data = models.JSONField(blank=True, null=True)
    payment_method = models.CharField(max_length=25, default='')
    status = models.CharField(max_length=15, choices=STATUS, default='New')
    is_ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.order_number

    @property
    def name(self):
        return f'{self.first_name} {self.last_name}'

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def sub_total(self):
        return self.price * self.quantity

    def __str__(self):
        return f"{self.quantity} x {self.dish.name}"
