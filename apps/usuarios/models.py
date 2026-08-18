from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from datetime import timedelta
import secrets


class Rol(models.Model):
    NOMBRES = [
        ('admin', 'Administrador'),
        ('recepcion', 'Recepción'),
        ('groomer', 'Groomer'),
        ('cliente', 'Cliente'),
    ]
    nombre      = models.CharField(max_length=50, unique=True, choices=NOMBRES)
    descripcion = models.TextField(blank=True)

    def __str__(self):
        return self.get_nombre_display()


class Usuario(AbstractUser):
    rol                = models.ForeignKey(Rol, on_delete=models.SET_NULL, null=True, blank=True)
    telefono           = models.CharField(max_length=20, blank=True)
    email              = models.EmailField(unique=True)
    email_verificado   = models.BooleanField(default=False)
    token_activacion   = models.CharField(max_length=64, blank=True)
    token_expiracion   = models.DateTimeField(null=True, blank=True)
    intentos_fallidos  = models.IntegerField(default=0)
    bloqueado_hasta    = models.DateTimeField(null=True, blank=True)
    two_factor_secret  = models.CharField(max_length=32, blank=True)
    two_factor_activo  = models.BooleanField(default=False)
    ultimo_acceso      = models.DateTimeField(null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def __str__(self):
        return self.email

    def tiene_rol(self, nombre_rol):
        return self.rol and self.rol.nombre == nombre_rol

    def es_admin(self):
        return self.tiene_rol('admin')

    def es_recepcion(self):
        return self.tiene_rol('recepcion')

    def es_groomer(self):
        return self.tiene_rol('groomer')

    def es_cliente(self):
        return self.tiene_rol('cliente')

    def esta_bloqueado(self):
        if self.bloqueado_hasta and self.bloqueado_hasta > timezone.now():
            return True
        return False

    def generar_token_activacion(self):
        self.token_activacion = secrets.token_urlsafe(32)
        self.token_expiracion = timezone.now() + timedelta(minutes=15)
        self.save(update_fields=['token_activacion', 'token_expiracion'])
        return self.token_activacion

    def token_valido(self):
        return self.token_expiracion and self.token_expiracion > timezone.now()

    def registrar_intento_fallido(self):
        self.intentos_fallidos += 1
        if self.intentos_fallidos >= 5:
            self.bloqueado_hasta = timezone.now() + timedelta(minutes=15)
        self.save(update_fields=['intentos_fallidos', 'bloqueado_hasta'])

    def limpiar_intentos(self):
        self.intentos_fallidos = 0
        self.bloqueado_hasta = None
        self.ultimo_acceso = timezone.now()
        self.save(update_fields=['intentos_fallidos', 'bloqueado_hasta', 'ultimo_acceso'])


class SesionUsuario(models.Model):
    usuario          = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='sesiones')
    token_jwt        = models.TextField()
    refresh_token    = models.CharField(max_length=64)
    ip_address       = models.GenericIPAddressField()
    user_agent       = models.TextField()
    fecha_expiracion = models.DateTimeField()
    creado_en        = models.DateTimeField(auto_now_add=True)

    def esta_activa(self):
        return self.fecha_expiracion > timezone.now()

    def __str__(self):
        return f"Sesión de {self.usuario.email} desde {self.ip_address}"


class LogAuditoria(models.Model):
    usuario    = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True)
    accion     = models.CharField(max_length=255)
    detalle    = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    fecha      = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha']
        verbose_name = 'Log de Auditoría'

    def __str__(self):
        return f"{self.fecha} | {self.usuario} | {self.accion}"
