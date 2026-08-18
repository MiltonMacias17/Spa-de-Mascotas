from django.urls import path
from . import views

app_name = 'facturacion'

urlpatterns = [
    path('', views.lista_facturas, name='lista'),
    path('<int:pk>/', views.detalle_factura, name='detalle'),
    path('cita/<int:cita_id>/crear/', views.crear_factura_cita, name='crear_cita'),
]
