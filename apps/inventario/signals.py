from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Producto


@receiver(post_save, sender=Producto)
def alerta_bajo_stock(sender, instance, **kwargs):
    if instance.stock_actual <= instance.stock_minimo:
        from apps.notificaciones.models import Notificacion
        from apps.usuarios.models import Usuario, Rol
        from django.utils import timezone

        admins = Usuario.objects.filter(rol__nombre='admin', is_active=True)
        for admin in admins:
            ya_notificado = Notificacion.objects.filter(
                destinatario=admin,
                tipo_evento='bajo_stock',
                exitoso=False,
                cita=None,
                fecha_programacion__date=timezone.now().date(),
                mensaje__contains=instance.nombre,
            ).exists()
            if not ya_notificado:
                Notificacion.objects.create(
                    destinatario=admin,
                    tipo_canal='email',
                    tipo_evento='bajo_stock',
                    destino=admin.email,
                    mensaje=f'Stock bajo: {instance.nombre} — actual: {instance.stock_actual}, mínimo: {instance.stock_minimo}',
                    fecha_programacion=timezone.now(),
                )
