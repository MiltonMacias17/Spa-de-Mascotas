from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from apps.usuarios.decorators import login_requerido, requiere_rol
from .models import FichaGrooming, ChecklistItem, FotoServicio, ItemChecklistTemplate
from apps.agenda.models import Cita


@login_requerido
@requiere_rol('admin', 'recepcion', 'groomer')
def ficha_grooming(request, pk):
    ficha = get_object_or_404(FichaGrooming, pk=pk)
    if request.user.es_groomer():
        try:
            if ficha.cita.groomer != request.user.groomer:
                messages.error(request, 'No tienes permiso para ver esta ficha.')
                return redirect('agenda:calendario')
        except Exception:
            return redirect('agenda:calendario')

    checklist = ficha.checklist_items.select_related('item').all()
    fotos     = ficha.fotos.all()

    if request.method == 'POST':
        accion = request.POST.get('accion')
        if accion == 'actualizar_estado':
            ficha.estado_ingreso = request.POST.get('estado_ingreso', '')
            ficha.temperatura_animal = request.POST.get('temperatura', '') or None
            ficha.notas_internas = request.POST.get('notas_internas', '')
            ficha.recomendaciones = request.POST.get('recomendaciones', '')
            ficha.save()
            ficha.cita.estado = 'en_progreso'
            ficha.cita.save(update_fields=['estado'])
            messages.success(request, 'Ficha actualizada.')

    return render(request, 'grooming/ficha.html', {
        'ficha': ficha,
        'checklist': checklist,
        'fotos': fotos,
    })


@login_requerido
@requiere_rol('admin', 'groomer')
def actualizar_checklist(request, pk):
    ficha = get_object_or_404(FichaGrooming, pk=pk)
    if request.method == 'POST':
        for item in ficha.checklist_items.all():
            completado  = request.POST.get(f'item_{item.pk}') == 'on'
            observacion = request.POST.get(f'obs_{item.pk}', '')
            item.completado  = completado
            item.observacion = observacion
            item.save()
        messages.success(request, 'Checklist guardado.')
    return redirect('grooming:ficha', pk=pk)


@login_requerido
@requiere_rol('admin', 'groomer')
def subir_fotos(request, pk):
    ficha = get_object_or_404(FichaGrooming, pk=pk)
    if request.method == 'POST':
        momento = request.POST.get('momento')
        imagen  = request.FILES.get('imagen')
        if imagen and momento in ['antes', 'despues']:
            FotoServicio.objects.create(ficha=ficha, imagen=imagen, momento=momento)
            messages.success(request, f'Foto "{momento}" subida correctamente.')
        else:
            messages.error(request, 'Debes seleccionar una imagen y el momento.')
    return redirect('grooming:ficha', pk=pk)


@login_requerido
@requiere_rol('admin', 'groomer')
def cerrar_ficha(request, pk):
    ficha = get_object_or_404(FichaGrooming, pk=pk)

    if ficha.fecha_cierre:
        messages.info(request, 'Esta ficha ya está cerrada.')
        return redirect('grooming:ficha', pk=pk)

    if not ficha.checklist_completo():
        messages.error(request, 'Debes completar al menos 5 ítems del checklist antes de cerrar.')
        return redirect('grooming:ficha', pk=pk)

    if not ficha.fotos.filter(momento='antes').exists():
        messages.error(request, 'Debes subir al menos una foto del estado inicial (antes).')
        return redirect('grooming:ficha', pk=pk)

    if not ficha.fotos.filter(momento='despues').exists():
        messages.error(request, 'Debes subir al menos una foto del resultado (después).')
        return redirect('grooming:ficha', pk=pk)

    # Descontar insumos del inventario
    if not ficha.consumido_inventario:
        consumo = ficha.cita.servicio.consumo_insumos
        from apps.inventario.models import Producto, MovimientoInventario
        for sku, cantidad in consumo.items():
            try:
                producto = Producto.objects.get(sku=sku)
                stock_antes = producto.stock_actual
                producto.descontar_stock(int(cantidad))
                MovimientoInventario.objects.create(
                    producto=producto,
                    tipo='salida_grooming',
                    cantidad=int(cantidad),
                    stock_tras=producto.stock_actual,
                    referencia=f'Ficha #{ficha.pk}',
                )
            except Exception:
                pass
        ficha.consumido_inventario = True

    ficha.fecha_cierre = timezone.now()
    ficha.save()

    ficha.cita.estado = 'completada'
    ficha.cita.duracion_real = int((ficha.fecha_cierre - ficha.cita.fecha_hora_inicio).total_seconds() / 60)
    ficha.cita.save(update_fields=['estado', 'duracion_real'])

    # Registrar en historial
    from apps.mascotas.models import HistorialMascota
    HistorialMascota.objects.create(
        mascota=ficha.cita.mascota,
        tipo_evento='servicio',
        descripcion=f'Servicio completado: {ficha.cita.servicio.nombre}. Recomendaciones: {ficha.recomendaciones}',
        creado_por=request.user,
    )

    # Notificación "Listo para recoger"
    from apps.notificaciones.models import Notificacion
    dueno = ficha.cita.mascota.mascotadueno_set.filter(es_dueno_principal=True).first()
    if dueno:
        Notificacion.objects.create(
            destinatario=dueno.cliente.usuario,
            tipo_canal=dueno.cliente.canal_notificacion,
            tipo_evento='listo_recoger',
            destino=dueno.cliente.usuario.email,
            mensaje=f'¡{ficha.cita.mascota.nombre} está listo/a para ser recogido/a! Servicio: {ficha.cita.servicio.nombre}.',
            fecha_programacion=timezone.now(),
            cita=ficha.cita,
        )

    messages.success(request, f'Ficha cerrada. {ficha.cita.mascota.nombre} listo/a para ser recogido/a.')
    return redirect('agenda:calendario')
