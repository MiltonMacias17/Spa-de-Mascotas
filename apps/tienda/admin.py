from django.contrib import admin
from .models import Carrito, DetalleCarrito, Pedido, DetallePedido


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ['pk', 'cliente', 'total', 'estado', 'creado_en']
    list_filter  = ['estado', 'metodo_contacto']
