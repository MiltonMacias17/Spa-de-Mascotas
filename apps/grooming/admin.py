from django.contrib import admin
from .models import ItemChecklistTemplate, FichaGrooming, ChecklistItem, FotoServicio


@admin.register(ItemChecklistTemplate)
class ItemTemplateAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'servicio', 'requiere_observacion']


@admin.register(FichaGrooming)
class FichaGroomingAdmin(admin.ModelAdmin):
    list_display  = ['cita', 'fecha_apertura', 'fecha_cierre', 'consumido_inventario']
    list_filter   = ['consumido_inventario']
    readonly_fields = ['fecha_apertura']
