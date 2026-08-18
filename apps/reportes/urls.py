from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard, name='inicio'),
    path('reportes/ocupacion/', views.reporte_ocupacion, name='ocupacion'),
]
