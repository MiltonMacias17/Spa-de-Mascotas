from django.contrib import admin
from .models import Servicio, Groomer, Cita, DisponibilidadGroomer, BloqueoCalendario


@admin.register(Servicio)
class ServicioAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'duracion_base_minutos', 'precio_base', 'activo']
    list_filter  = ['activo']


@admin.register(Groomer)
class GroomerAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'especialidad', 'capacidad_simultanea', 'esta_activo']


@admin.register(Cita)
class CitaAdmin(admin.ModelAdmin):
    list_display = ['mascota', 'groomer', 'servicio', 'fecha_hora_inicio', 'estado']
    list_filter  = ['estado', 'groomer']
    date_hierarchy = 'fecha_hora_inicio'


@admin.register(BloqueoCalendario)
class BloqueoAdmin(admin.ModelAdmin):
    list_display = ['tipo', 'groomer', 'fecha_inicio', 'fecha_fin']
