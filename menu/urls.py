from django.urls import path
from . import views
from .views import menu_modify

urlpatterns = [
    path('', views.menu, name='menu'),
    path('modify/', menu_modify, name='menu_modify')
]
