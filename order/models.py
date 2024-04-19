from django.db import models
from django.contrib.auth.models import User
from coupon import models as coupon

# Create your models here.
class Order(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    total = models.FloatField()
    qtd_total = models.PositiveIntegerField()
    applied_coupon = models.ForeignKey(coupon.Coupon, on_delete = models.DO_NOTHING, blank=True, null=True)
    status = models.CharField(
        default = 'C',
        max_length = 1,
        choices = (
            ('A', 'Approved'),
            ('C', 'Created'),
            ('D', 'Disapproved'),
            ('P', 'Pending'),
            ('S', 'Sended'),
            ('F', 'Finished')
        )
    )


    def __str__(self):
        return f'Order number: {self.pk}'


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.CharField(max_length=255)
    product_id = models.PositiveIntegerField()
    variation = models.CharField(max_length=255)
    variation_id = models.CharField(max_length=50)
    price = models.FloatField()
    promotional_price = models.FloatField(default=0)
    quantity = models.PositiveIntegerField()
    image = models.CharField(max_length=2000)

    def __str__(self):
        return f'Item of {self.order}'
    
    class Meta:
        verbose_name = 'Order item'
        verbose_name_plural = 'Order items'