from django.urls import path
from . import views

app_name = 'tienda'

urlpatterns = [
    path('', views.catalogo, name='catalogo'),
    path('producto/<int:pk>/', views.detalle_producto, name='producto'),
    path('carrito/', views.ver_carrito, name='carrito'),
    path('carrito/agregar/', views.agregar_al_carrito, name='agregar'),
    path('carrito/quitar/<int:item_id>/', views.quitar_del_carrito, name='quitar'),
    path('carrito/pedido-whatsapp/', views.pedido_whatsapp, name='pedido_whatsapp'),
]
