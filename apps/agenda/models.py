from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from apps.usuarios.models import Usuario
from apps.mascotas.models import Mascota


class Servicio(models.Model):
    nombre                       = models.CharField(max_length=100)
    descripcion                  = models.TextField(blank=True)
    duracion_base_minutos        = models.IntegerField(default=60)
    precio_base                  = models.DecimalField(max_digits=8, decimal_places=2)
    permite_doble_booking        = models.BooleanField(default=False)
    requiere_bloqueo_consecutivo = models.BooleanField(default=False)
    factor_tamanio_raza          = models.JSONField(default=dict, blank=True)
    consumo_insumos              = models.JSONField(default=dict, blank=True)
    activo                       = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nombre} ({self.duracion_base_minutos} min)"

    def duracion_para_tamanio(self, tamanio):
        factores = {'pequeno': 1.0, 'mediano': 1.10, 'grande': 1.15, 'gigante': 1.30}
        factor = factores.get(tamanio, 1.0)
        return int(self.duracion_base_minutos * factor)


class Groomer(models.Model):
    usuario              = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='groomer')
    especialidad         = models.CharField(max_length=100, blank=True)
    capacidad_simultanea = models.IntegerField(default=1)
    horario_trabajo      = models.JSONField(default=dict, blank=True)
    esta_activo          = models.BooleanField(default=True)

    def __str__(self):
        return f"Groomer: {self.usuario.get_full_name() or self.usuario.email}"


class DisponibilidadGroomer(models.Model):
    DIAS = [
        (0, 'Domingo'), (1, 'Lunes'), (2, 'Martes'), (3, 'Miércoles'),
        (4, 'Jueves'), (5, 'Viernes'), (6, 'Sábado'),
    ]
    groomer            = models.ForeignKey(Groomer, on_delete=models.CASCADE, related_name='disponibilidades')
    dia_semana         = models.IntegerField(choices=DIAS)
    hora_inicio        = models.TimeField()
    hora_fin           = models.TimeField()
    intervalo_descanso = models.JSONField(default=dict, blank=True)

    class Meta:
        unique_together = ('groomer', 'dia_semana')

    def __str__(self):
        return f"{self.groomer} | {self.get_dia_semana_display()} {self.hora_inicio}-{self.hora_fin}"


class BloqueoCalendario(models.Model):
    TIPO = [
        ('feriado', 'Feriado'),
        ('mantenimiento', 'Mantenimiento'),
        ('vacaciones', 'Vacaciones'),
        ('ausencia', 'Ausencia'),
    ]
    tipo         = models.CharField(max_length=20, choices=TIPO)
    fecha_inicio = models.DateTimeField()
    fecha_fin    = models.DateTimeField()
    groomer      = models.ForeignKey(Groomer, null=True, blank=True, on_delete=models.SET_NULL)
    descripcion  = models.TextField(blank=True)

    def clean(self):
        if self.fecha_fin <= self.fecha_inicio:
            raise ValidationError('La fecha fin debe ser posterior a la fecha inicio.')

    def __str__(self):
        target = self.groomer or 'Global'
        return f"{self.get_tipo_display()} ({target}) {self.fecha_inicio.date()}"


class Cita(models.Model):
    ESTADO = [
        ('agendada', 'Agendada'),
        ('confirmada', 'Confirmada'),
        ('en_progreso', 'En Progreso'),
        ('completada', 'Completada'),
        ('cancelada', 'Cancelada'),
        ('no_asistio', 'No Asistió'),
    ]
    mascota              = models.ForeignKey(Mascota, on_delete=models.CASCADE, related_name='citas')
    groomer              = models.ForeignKey(Groomer, on_delete=models.PROTECT, related_name='citas')
    servicio             = models.ForeignKey(Servicio, on_delete=models.PROTECT)
    fecha_hora_inicio    = models.DateTimeField()
    fecha_hora_fin       = models.DateTimeField()
    duracion_real        = models.IntegerField(null=True, blank=True)
    estado               = models.CharField(max_length=20, choices=ESTADO, default='agendada')
    creado_por           = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True,
                               related_name='citas_creadas')
    reprogramado_por     = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True,
                               related_name='citas_reprogramadas')
    fecha_reprogramacion = models.DateTimeField(null=True, blank=True)
    notas                = models.TextField(blank=True)
    precio_calculado     = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    creado_en            = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['fecha_hora_inicio']

    def clean(self):
        if self.fecha_hora_fin and self.fecha_hora_inicio:
            if self.fecha_hora_fin <= self.fecha_hora_inicio:
                raise ValidationError('La hora de fin debe ser posterior a la hora de inicio.')

    def __str__(self):
        return f"{self.mascota.nombre} | {self.servicio.nombre} | {self.fecha_hora_inicio}"

    def duracion_minutos(self):
        delta = self.fecha_hora_fin - self.fecha_hora_inicio
        return int(delta.total_seconds() / 60)
