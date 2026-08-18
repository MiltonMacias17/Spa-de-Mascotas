from django.contrib import admin
from .models import Categoria, Producto, VarianteProducto, MovimientoInventario


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'padre']


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display  = ['nombre', 'sku', 'precio_base', 'stock_actual', 'stock_minimo', 'es_insumo', 'activo']
    list_filter   = ['es_insumo', 'activo', 'categoria']
    search_fields = ['nombre', 'sku']


@admin.register(MovimientoInventario)
class MovimientoAdmin(admin.ModelAdmin):
    list_display  = ['producto', 'tipo', 'cantidad', 'stock_tras', 'fecha']
    list_filter   = ['tipo']
    readonly_fields = ['fecha']
