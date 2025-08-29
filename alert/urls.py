from django.urls import path
from . import views

urlpatterns = [
    path('', views.alert, name='alert'),
    path('create/', views.alert_new, name='create'),
    path('<int:pk>/extend/', views.alert_extend, name='extend'),
    path('<int:pk>/deactivate/', views.alert_deactivate, name='deactivate'),
]
