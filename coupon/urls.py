from django.urls import path
from . import views

app_name = 'coupon'

urlpatterns = [
    path('coupon/', views.AttachCoupon.as_view(), name='coupon'),
    path('removecoupon/', views.RemoveCoupon.as_view(), name='removecoupon'),
]
