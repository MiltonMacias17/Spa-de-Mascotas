from django.contrib import admin
from .models import Factura, DetalleFactura, Pago


class DetalleInline(admin.TabularInline):
    model = DetalleFactura
    extra = 0


class PagoInline(admin.TabularInline):
    model = Pago
    extra = 0


@admin.register(Factura)
class FacturaAdmin(admin.ModelAdmin):
    list_display = ['numero_secuencial', 'cliente', 'total', 'estado', 'metodo_pago', 'fecha_emision']
    list_filter  = ['estado', 'metodo_pago']
    inlines      = [DetalleInline, PagoInline]
