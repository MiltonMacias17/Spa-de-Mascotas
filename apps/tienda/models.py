from django.db import models
from django.utils import timezone
from apps.mascotas.models import Cliente
from apps.inventario.models import Producto, VarianteProducto
import secrets


class Carrito(models.Model):
    usuario       = models.ForeignKey('usuarios.Usuario', null=True, blank=True,
                        on_delete=models.SET_NULL, related_name='carritos')
    session_token = models.CharField(max_length=64, unique=True)
    expires_at    = models.DateTimeField()
    creado_en     = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.session_token:
            self.session_token = secrets.token_urlsafe(32)
        if not self.expires_at:
            self.expires_at = timezone.now() + timezone.timedelta(days=7)
        super().save(*args, **kwargs)

    def total(self):
        return sum(item.subtotal() for item in self.items.all())

    def cantidad_items(self):
        return sum(item.cantidad for item in self.items.all())

    def __str__(self):
        return f"Carrito {self.session_token[:8]}..."


class DetalleCarrito(models.Model):
    carrito         = models.ForeignKey(Carrito, on_delete=models.CASCADE, related_name='items')
    producto        = models.ForeignKey(Producto, on_delete=models.PROTECT)
    variante        = models.ForeignKey(VarianteProducto, null=True, blank=True, on_delete=models.SET_NULL)
    cantidad        = models.PositiveIntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=8, decimal_places=2)

    def subtotal(self):
        return self.precio_unitario * self.cantidad

    def __str__(self):
        return f"{self.cantidad}x {self.producto.nombre}"


class Pedido(models.Model):
    ESTADO = [
        ('pendiente', 'Pendiente'),
        ('enviado', 'Enviado'),
        ('confirmado', 'Confirmado'),
        ('pagado', 'Pagado'),
        ('entregado', 'Entregado'),
    ]
    CONTACTO = [('whatsapp', 'WhatsApp'), ('telegram', 'Telegram')]
    carrito         = models.ForeignKey(Carrito, on_delete=models.PROTECT)
    cliente         = models.ForeignKey(Cliente, on_delete=models.PROTECT)
    subtotal        = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    descuento       = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    total           = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    metodo_contacto = models.CharField(max_length=20, choices=CONTACTO, default='whatsapp')
    estado          = models.CharField(max_length=20, choices=ESTADO, default='pendiente')
    creado_en       = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Pedido #{self.pk} - {self.cliente.nombre}"


class DetallePedido(models.Model):
    pedido          = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='items')
    producto        = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad        = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=8, decimal_places=2)

    def subtotal(self):
        return self.precio_unitario * self.cantidad
