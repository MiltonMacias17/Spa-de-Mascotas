from django.db import models


class Categoria(models.Model):
    nombre = models.CharField(max_length=100)
    padre  = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='subcategorias')

    def __str__(self):
        if self.padre:
            return f"{self.padre.nombre} > {self.nombre}"
        return self.nombre

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.pk and self.padre and self.padre.pk == self.pk:
            raise ValidationError('Una categoría no puede ser su propio padre.')


class Producto(models.Model):
    nombre       = models.CharField(max_length=200)
    descripcion  = models.TextField(blank=True)
    categoria    = models.ForeignKey(Categoria, on_delete=models.PROTECT)
    precio_base  = models.DecimalField(max_digits=8, decimal_places=2)
    stock_actual = models.IntegerField(default=0)
    stock_minimo = models.IntegerField(default=5)
    sku          = models.CharField(max_length=50, unique=True)
    imagen       = models.ImageField(upload_to='productos/', blank=True)
    es_insumo    = models.BooleanField(default=False)
    activo       = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nombre} (stock: {self.stock_actual})"

    def bajo_stock(self):
        return self.stock_actual <= self.stock_minimo

    def descontar_stock(self, cantidad):
        if self.stock_actual < cantidad:
            raise ValueError(f'Stock insuficiente para {self.nombre}')
        self.stock_actual -= cantidad
        self.save(update_fields=['stock_actual'])


class VarianteProducto(models.Model):
    producto     = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='variantes')
    atributo     = models.CharField(max_length=50)
    valor        = models.CharField(max_length=50)
    precio_extra = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    stock        = models.IntegerField(default=0)
    sku_variante = models.CharField(max_length=60, unique=True)

    def __str__(self):
        return f"{self.producto.nombre} - {self.atributo}: {self.valor}"

    def precio_total(self):
        return self.producto.precio_base + self.precio_extra


class MovimientoInventario(models.Model):
    TIPO = [
        ('entrada', 'Entrada'),
        ('salida_grooming', 'Salida Grooming'),
        ('salida_venta', 'Salida Venta'),
        ('ajuste', 'Ajuste'),
        ('devolucion', 'Devolución'),
    ]
    producto   = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='movimientos')
    tipo       = models.CharField(max_length=20, choices=TIPO)
    cantidad   = models.IntegerField()
    stock_tras = models.IntegerField()
    referencia = models.CharField(max_length=100, blank=True)
    nota       = models.TextField(blank=True)
    fecha      = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.tipo} {self.cantidad}x {self.producto.nombre}"
