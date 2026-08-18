from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario, Rol, SesionUsuario, LogAuditoria


@admin.register(Rol)
class RolAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'descripcion']


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display  = ['email', 'first_name', 'last_name', 'rol', 'email_verificado', 'is_active']
    list_filter   = ['rol', 'email_verificado', 'is_active']
    search_fields = ['email', 'first_name', 'last_name']
    ordering      = ['email']
    fieldsets = UserAdmin.fieldsets + (
        ('Pet Spa', {'fields': ('rol', 'telefono', 'email_verificado',
                                'two_factor_activo', 'ultimo_acceso')}),
    )


@admin.register(LogAuditoria)
class LogAuditoriaAdmin(admin.ModelAdmin):
    list_display  = ['fecha', 'usuario', 'accion', 'ip_address']
    list_filter   = ['accion']
    search_fields = ['usuario__email', 'accion']
    readonly_fields = ['fecha', 'usuario', 'accion', 'ip_address', 'user_agent', 'detalle']
