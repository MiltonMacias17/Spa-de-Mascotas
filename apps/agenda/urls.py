from django.urls import path
from . import views

app_name = 'agenda'

urlpatterns = [
    path('', views.calendario, name='calendario'),
    path('cita/nueva/', views.nueva_cita, name='nueva_cita'),
    path('cita/<int:pk>/', views.detalle_cita, name='detalle_cita'),
    path('cita/<int:pk>/cancelar/', views.cancelar_cita, name='cancelar_cita'),
    path('cita/<int:pk>/confirmar/', views.confirmar_cita, name='confirmar_cita'),
    path('bloqueos/', views.gestionar_bloqueos, name='bloqueos'),
    path('api/slots/', views.slots_disponibles, name='slots_disponibles'),
]
