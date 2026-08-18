from django.contrib import admin
from .models import Cliente, Mascota, MascotaDueno, Vacuna, HistorialMascota


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display  = ['nombre', 'ci', 'usuario', 'canal_notificacion']
    search_fields = ['nombre', 'ci', 'usuario__email']


@admin.register(Mascota)
class MascotaAdmin(admin.ModelAdmin):
    list_display  = ['nombre', 'especie', 'raza', 'tamanio', 'activa']
    list_filter   = ['especie', 'tamanio', 'activa']
    search_fields = ['nombre', 'raza']


@admin.register(HistorialMascota)
class HistorialAdmin(admin.ModelAdmin):
    list_display = ['mascota', 'tipo_evento', 'fecha']
    list_filter  = ['tipo_evento']
