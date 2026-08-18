from django.db import models
from django.core.exceptions import ValidationError
from apps.agenda.models import Cita, Servicio


class ItemChecklistTemplate(models.Model):
    nombre               = models.CharField(max_length=100)
    requiere_observacion = models.BooleanField(default=False)
    servicio             = models.ForeignKey(Servicio, on_delete=models.CASCADE,
                               null=True, blank=True, related_name='checklist_items')

    def __str__(self):
        return self.nombre


class FichaGrooming(models.Model):
    cita                 = models.OneToOneField(Cita, on_delete=models.CASCADE, related_name='ficha')
    raza_al_momento      = models.CharField(max_length=100, blank=True)
    tamanio_al_momento   = models.CharField(max_length=20, blank=True)
    temperatura_animal   = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    estado_ingreso       = models.TextField(blank=True)
    notas_internas       = models.TextField(blank=True)
    recomendaciones      = models.TextField(blank=True)
    consumido_inventario = models.BooleanField(default=False)
    fecha_apertura       = models.DateTimeField(auto_now_add=True)
    fecha_cierre         = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Ficha #{self.pk} - {self.cita.mascota.nombre}"

    def checklist_completo(self):
        items = self.checklist_items.all()
        if not items.exists():
            return False
        completados = items.filter(completado=True).count()
        return completados >= max(5, items.count() // 2)

    def puede_cerrar(self):
        tiene_fotos_antes = self.fotos.filter(momento='antes').exists()
        tiene_fotos_despues = self.fotos.filter(momento='despues').exists()
        return self.checklist_completo() and tiene_fotos_antes and tiene_fotos_despues


class ChecklistItem(models.Model):
    ficha       = models.ForeignKey(FichaGrooming, on_delete=models.CASCADE, related_name='checklist_items')
    item        = models.ForeignKey(ItemChecklistTemplate, on_delete=models.PROTECT)
    completado  = models.BooleanField(default=False)
    observacion = models.TextField(blank=True)

    class Meta:
        unique_together = ('ficha', 'item')

    def __str__(self):
        estado = '✓' if self.completado else '○'
        return f"{estado} {self.item.nombre}"


class FotoServicio(models.Model):
    MOMENTO = [('antes', 'Antes'), ('despues', 'Después')]
    ficha     = models.ForeignKey(FichaGrooming, on_delete=models.CASCADE, related_name='fotos')
    imagen    = models.ImageField(upload_to='mascotas/fotos/')
    momento   = models.CharField(max_length=10, choices=MOMENTO)
    subida_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Foto {self.momento} - Ficha #{self.ficha.pk}"
