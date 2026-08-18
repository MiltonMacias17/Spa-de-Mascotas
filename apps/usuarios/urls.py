from django.urls import path
from . import views

app_name = 'usuarios'

urlpatterns = [
    path('login/', views.vista_login, name='login'),
    path('logout/', views.vista_logout, name='logout'),
    path('registro/', views.vista_registro, name='registro'),
    path('activar/<str:token>/', views.activar_cuenta, name='activar'),
    path('recuperar/', views.recuperar_password, name='recuperar_password'),
    path('reset/<str:token>/', views.reset_password, name='reset_password'),
    path('2fa/verificar/', views.verificar_2fa, name='verificar_2fa'),
    path('2fa/setup/', views.setup_2fa, name='setup_2fa'),
    path('perfil/', views.perfil, name='perfil'),
]
