from django.db import models
from apps.usuarios.models import Usuario


class Cliente(models.Model):
    CANAL = [('email', 'Email'), ('whatsapp', 'WhatsApp'), ('sms', 'SMS')]
    usuario            = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='cliente')
    nombre             = models.CharField(max_length=100)
    ci                 = models.CharField(max_length=20, unique=True)
    direccion          = models.TextField(blank=True)
    telefono           = models.CharField(max_length=20, blank=True)
    canal_notificacion = models.CharField(max_length=20, choices=CANAL, default='email')
    creado_en          = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} ({self.usuario.email})"


class Mascota(models.Model):
    TAMANIO = [
        ('pequeno', 'Pequeño'),
        ('mediano', 'Mediano'),
        ('grande', 'Grande'),
        ('gigante', 'Gigante'),
    ]
    TEMPERAMENTO = [
        ('tranquilo', 'Tranquilo'),
        ('nervioso', 'Nervioso'),
        ('agresivo', 'Agresivo'),
        ('inquieto', 'Inquieto'),
    ]
    duenos           = models.ManyToManyField(Cliente, through='MascotaDueno', related_name='mascotas')
    nombre           = models.CharField(max_length=100)
    especie          = models.CharField(max_length=50)
    raza             = models.CharField(max_length=100)
    tamanio          = models.CharField(max_length=20, choices=TAMANIO)
    fecha_nacimiento = models.DateField()
    alergias         = models.TextField(blank=True)
    temperamento     = models.CharField(max_length=20, choices=TEMPERAMENTO, default='tranquilo')
    peso_kg          = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    restricciones    = models.TextField(blank=True)
    foto_perfil      = models.ImageField(upload_to='mascotas/perfil/', blank=True)
    activa           = models.BooleanField(default=True)
    creado_en        = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} ({self.especie} - {self.raza})"

    def edad_texto(self):
        from datetime import date
        today = date.today()
        delta = today - self.fecha_nacimiento
        years = delta.days // 365
        months = (delta.days % 365) // 30
        if years > 0:
            return f"{years} año(s)"
        return f"{months} mes(es)"


class MascotaDueno(models.Model):
    mascota            = models.ForeignKey(Mascota, on_delete=models.CASCADE)
    cliente            = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    es_dueno_principal = models.BooleanField(default=False)

    class Meta:
        unique_together = ('mascota', 'cliente')


class Vacuna(models.Model):
    mascota          = models.ForeignKey(Mascota, on_delete=models.CASCADE, related_name='vacunas')
    nombre           = models.CharField(max_length=100)
    fecha_aplicacion = models.DateField()
    fecha_vencimiento = models.DateField(null=True, blank=True)
    veterinario      = models.CharField(max_length=100, blank=True)
    documento        = models.FileField(upload_to='mascotas/vacunas/', blank=True)

    def __str__(self):
        return f"{self.nombre} - {self.mascota.nombre}"


class HistorialMascota(models.Model):
    TIPO = [
        ('servicio', 'Servicio'),
        ('recomendacion', 'Recomendación'),
        ('alerta', 'Alerta'),
        ('cancelacion', 'Cancelación'),
        ('vacuna', 'Vacuna'),
    ]
    mascota     = models.ForeignKey(Mascota, on_delete=models.CASCADE, related_name='historial')
    tipo_evento = models.CharField(max_length=30, choices=TIPO)
    descripcion = models.TextField()
    fecha       = models.DateTimeField(auto_now_add=True)
    creado_por  = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['-fecha']

    def __str__(self):
        return f"{self.tipo_evento} - {self.mascota.nombre} ({self.fecha.date()})"
