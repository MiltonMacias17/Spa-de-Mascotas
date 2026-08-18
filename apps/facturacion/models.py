from django.db import models
from apps.mascotas.models import Cliente


class Factura(models.Model):
    ESTADO = [('pendiente', 'Pendiente'), ('pagada', 'Pagada'), ('cancelada', 'Cancelada')]
    METODO = [('efectivo', 'Efectivo'), ('qr', 'QR'), ('transferencia', 'Transferencia')]

    numero_secuencial = models.AutoField(primary_key=True)
    cita    = models.ForeignKey('agenda.Cita', null=True, blank=True,
                  on_delete=models.SET_NULL, related_name='facturas')
    pedido  = models.ForeignKey('tienda.Pedido', null=True, blank=True,
                  on_delete=models.SET_NULL, related_name='facturas')
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT)
    subtotal     = models.DecimalField(max_digits=10, decimal_places=2)
    impuesto     = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    total        = models.DecimalField(max_digits=10, decimal_places=2)
    estado       = models.CharField(max_length=20, choices=ESTADO, default='pendiente')
    metodo_pago  = models.CharField(max_length=20, choices=METODO, default='efectivo')
    notas        = models.TextField(blank=True)
    fecha_emision = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha_emision']

    def __str__(self):
        return f"Factura #{self.numero_secuencial} - {self.cliente.nombre}"

    def save(self, *args, **kwargs):
        if not self.total:
            self.total = self.subtotal + self.impuesto
        super().save(*args, **kwargs)


class DetalleFactura(models.Model):
    factura         = models.ForeignKey(Factura, on_delete=models.CASCADE, related_name='items')
    descripcion     = models.CharField(max_length=200)
    cantidad        = models.PositiveIntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=8, decimal_places=2)

    def subtotal(self):
        return self.precio_unitario * self.cantidad

    def __str__(self):
        return f"{self.descripcion} x{self.cantidad}"


class Pago(models.Model):
    ESTADO = [('completado', 'Completado'), ('pendiente', 'Pendiente'), ('fallido', 'Fallido')]
    factura               = models.ForeignKey(Factura, on_delete=models.CASCADE, related_name='pagos')
    monto                 = models.DecimalField(max_digits=10, decimal_places=2)
    referencia_transaccion = models.CharField(max_length=200, blank=True)
    estado                = models.CharField(max_length=20, choices=ESTADO, default='pendiente')
    fecha                 = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Pago {self.monto} - Factura #{self.factura.pk}"
