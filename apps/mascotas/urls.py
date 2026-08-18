from django.urls import path
from . import views

app_name = 'mascotas'

urlpatterns = [
    path('', views.lista_mascotas, name='lista'),
    path('nueva/', views.nueva_mascota, name='nueva'),
    path('<int:pk>/', views.detalle_mascota, name='detalle'),
    path('<int:pk>/editar/', views.editar_mascota, name='editar'),
    path('<int:pk>/eliminar/', views.eliminar_mascota, name='eliminar'),
    path('<int:pk>/historial/', views.historial_mascota, name='historial'),
]
