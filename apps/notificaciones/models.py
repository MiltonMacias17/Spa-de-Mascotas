from django.db import models
from apps.usuarios.models import Usuario


class Notificacion(models.Model):
    CANAL = [('email', 'Email'), ('whatsapp', 'WhatsApp'), ('sms', 'SMS')]
    EVENTO = [
        ('confirmacion', 'Confirmación de cita'),
        ('recordatorio_24h', 'Recordatorio 24h'),
        ('recordatorio_2h', 'Recordatorio 2h'),
        ('listo_recoger', 'Listo para recoger'),
        ('encuesta', 'Encuesta post-servicio'),
        ('bajo_stock', 'Alerta bajo stock'),
        ('bienvenida', 'Bienvenida'),
        ('activacion', 'Activación de cuenta'),
    ]
    destinatario       = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='notificaciones')
    tipo_canal         = models.CharField(max_length=20, choices=CANAL, default='email')
    tipo_evento        = models.CharField(max_length=30, choices=EVENTO)
    destino            = models.CharField(max_length=200)
    mensaje            = models.TextField()
    fecha_programacion = models.DateTimeField()
    fecha_envio        = models.DateTimeField(null=True, blank=True)
    exitoso            = models.BooleanField(default=False)
    intentos           = models.IntegerField(default=0)
    cita               = models.ForeignKey('agenda.Cita', null=True, blank=True,
                             on_delete=models.SET_NULL, related_name='notificaciones')

    class Meta:
        ordering = ['-fecha_programacion']

    def __str__(self):
        return f"{self.tipo_evento} → {self.destino}"
