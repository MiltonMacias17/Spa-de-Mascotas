from django.urls import path
from . import views

app_name = 'inventario'

urlpatterns = [
    path('', views.lista_productos, name='lista'),
    path('nuevo/', views.nuevo_producto, name='nuevo'),
    path('<int:pk>/editar/', views.editar_producto, name='editar'),
    path('<int:pk>/entrada/', views.entrada_inventario, name='entrada'),
    path('alertas/', views.alertas_inventario, name='alertas'),
]
