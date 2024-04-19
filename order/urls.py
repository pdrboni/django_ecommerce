from django.urls import path
from . import views

app_name = 'order'

urlpatterns = [
    path('pay/<int:pk>', views.OrderPayment.as_view(), name='payment'),
    path('saveorder/', views.SaveOrder.as_view(), name='saveorder'),
    path('details/<int:pk>', views.OrderDetails.as_view(), name='details'),
    path('list/', views.List.as_view(), name='list'),

]
