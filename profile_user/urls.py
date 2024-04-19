from django.urls import path
from . import views

app_name = 'profile_user'

urlpatterns = [
    path('', views.Create.as_view(), name='create'),
    path('edit/', views.Edit.as_view(), name='edit'),
    path('login/', views.Login.as_view(), name='login'),
    path('logout/', views.Logout.as_view(), name='logout'),
]
