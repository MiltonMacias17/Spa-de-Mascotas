from django.contrib import admin
from .models import Notificacion


@admin.register(Notificacion)
class NotificacionAdmin(admin.ModelAdmin):
    list_display  = ['tipo_evento', 'destinatario', 'tipo_canal', 'exitoso', 'fecha_programacion']
    list_filter   = ['tipo_evento', 'tipo_canal', 'exitoso']
    readonly_fields = ['fecha_envio', 'intentos']
