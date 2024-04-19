from django.contrib.auth.models import User
from django.db import models

# Create your models here.
class Coupon(models.Model):
    owner = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='Coupon owner')
    name = models.CharField(max_length=20)
    discount = models.FloatField(verbose_name='Discount')

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = 'Coupon'
        verbose_name_plural = 'Coupons'