from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from apps.usuarios.decorators import login_requerido, requiere_rol, no_clientes
from .models import Cita, Groomer, Servicio, DisponibilidadGroomer, BloqueoCalendario
from .forms import FormCita, FormBloqueo, FormDisponibilidad
from .validators import calcular_duracion, validar_slot_disponible
from apps.mascotas.models import Mascota
import json
from datetime import timedelta


@login_requerido
def calendario(request):
    if request.user.es_groomer():
        try:
            groomer = request.user.groomer
            citas = Cita.objects.filter(
                groomer=groomer,
                estado__in=['agendada', 'confirmada', 'en_progreso'],
                fecha_hora_inicio__gte=timezone.now() - timedelta(days=1),
            ).select_related('mascota', 'servicio')
        except Groomer.DoesNotExist:
            citas = Cita.objects.none()
        groomers = None
    else:
        citas = Cita.objects.filter(
            estado__in=['agendada', 'confirmada', 'en_progreso'],
            fecha_hora_inicio__gte=timezone.now() - timedelta(days=7),
        ).select_related('mascota', 'servicio', 'groomer')
        groomers = Groomer.objects.filter(esta_activo=True).select_related('usuario')

    eventos = []
    colores = {'agendada': '#4A90D9', 'confirmada': '#28A745', 'en_progreso': '#F5A623'}
    for cita in citas:
        eventos.append({
            'id': cita.pk,
            'title': f'{cita.mascota.nombre} — {cita.servicio.nombre}',
            'start': cita.fecha_hora_inicio.isoformat(),
            'end': cita.fecha_hora_fin.isoformat(),
            'color': colores.get(cita.estado, '#6c757d'),
            'url': f'/agenda/cita/{cita.pk}/',
        })

    return render(request, 'agenda/calendario.html', {
        'citas': citas,
        'groomers': groomers,
        'eventos_json': json.dumps(eventos),
    })


@login_requerido
@no_clientes
def nueva_cita(request):
    if request.method == 'POST':
        form = FormCita(request.POST)
        if form.is_valid():
            cita = form.save(commit=False)
            mascota  = form.cleaned_data['mascota']
            servicio = form.cleaned_data['servicio']
            groomer  = form.cleaned_data['groomer']

            duracion = calcular_duracion(servicio, mascota.tamanio)
            cita.fecha_hora_fin = cita.fecha_hora_inicio + timedelta(minutes=duracion)
            cita.precio_calculado = servicio.precio_base
            cita.creado_por = request.user

            errores = validar_slot_disponible(groomer, cita.fecha_hora_inicio, cita.fecha_hora_fin)
            if errores:
                for e in errores:
                    messages.error(request, e)
            else:
                cita.save()
                # Crear ficha de grooming automáticamente
                from apps.grooming.models import FichaGrooming, ItemChecklistTemplate, ChecklistItem
                ficha = FichaGrooming.objects.create(
                    cita=cita,
                    raza_al_momento=mascota.raza,
                    tamanio_al_momento=mascota.tamanio,
                )
                items_template = ItemChecklistTemplate.objects.filter(servicio=servicio)
                if not items_template.exists():
                    items_template = ItemChecklistTemplate.objects.all()
                for item in items_template:
                    ChecklistItem.objects.create(ficha=ficha, item=item)

                # Programar notificación de confirmación
                from apps.notificaciones.models import Notificacion
                dueno = mascota.mascotadueno_set.filter(es_dueno_principal=True).first()
                if dueno:
                    Notificacion.objects.create(
                        destinatario=dueno.cliente.usuario,
                        tipo_canal=dueno.cliente.canal_notificacion,
                        tipo_evento='confirmacion',
                        destino=dueno.cliente.usuario.email,
                        mensaje=f'Tu cita para {mascota.nombre} ({servicio.nombre}) fue confirmada para el {cita.fecha_hora_inicio.strftime("%d/%m/%Y %H:%M")}.',
                        fecha_programacion=timezone.now(),
                        cita=cita,
                    )

                messages.success(request, f'Cita creada para {mascota.nombre} el {cita.fecha_hora_inicio.strftime("%d/%m/%Y %H:%M")}.')
                return redirect('agenda:calendario')
    else:
        form = FormCita()

    servicios = Servicio.objects.filter(activo=True)
    return render(request, 'agenda/nueva_cita.html', {
        'form': form,
        'servicios': servicios,
        'servicios_json': json.dumps({
            str(s.pk): {'duracion': s.duracion_base_minutos, 'precio': float(s.precio_base)}
            for s in servicios
        }),
    })


@login_requerido
def detalle_cita(request, pk):
    cita = get_object_or_404(Cita, pk=pk)
    if request.user.es_groomer():
        try:
            if cita.groomer != request.user.groomer:
                messages.error(request, 'No tienes permiso para ver esta cita.')
                return redirect('agenda:calendario')
        except Groomer.DoesNotExist:
            return redirect('agenda:calendario')

    return render(request, 'agenda/detalle_cita.html', {'cita': cita})


@login_requerido
@no_clientes
def cancelar_cita(request, pk):
    cita = get_object_or_404(Cita, pk=pk)
    if request.method == 'POST':
        cita.estado = 'cancelada'
        cita.save(update_fields=['estado'])
        messages.success(request, 'Cita cancelada.')
        return redirect('agenda:calendario')
    return render(request, 'agenda/confirmar_cancelar.html', {'cita': cita})


@login_requerido
@no_clientes
def confirmar_cita(request, pk):
    cita = get_object_or_404(Cita, pk=pk, estado='agendada')
    cita.estado = 'confirmada'
    cita.save(update_fields=['estado'])
    messages.success(request, 'Cita confirmada.')
    return redirect('agenda:detalle_cita', pk=pk)


@login_requerido
@requiere_rol('admin', 'recepcion')
def gestionar_bloqueos(request):
    bloqueos = BloqueoCalendario.objects.order_by('-fecha_inicio')
    if request.method == 'POST':
        form = FormBloqueo(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Bloqueo registrado.')
            return redirect('agenda:bloqueos')
    else:
        form = FormBloqueo()
    return render(request, 'agenda/bloqueos.html', {'bloqueos': bloqueos, 'form': form})


def slots_disponibles(request):
    """API JSON: retorna slots libres para un groomer+servicio+fecha."""
    groomer_id  = request.GET.get('groomer')
    servicio_id = request.GET.get('servicio')
    fecha_str   = request.GET.get('fecha')
    if not all([groomer_id, servicio_id, fecha_str]):
        return JsonResponse({'slots': []})

    from datetime import datetime, date, time
    try:
        groomer  = Groomer.objects.get(pk=groomer_id)
        servicio = Servicio.objects.get(pk=servicio_id)
        fecha    = date.fromisoformat(fecha_str)
    except Exception:
        return JsonResponse({'slots': []})

    dia_modelo = (fecha.weekday() + 1) % 7
    disp = DisponibilidadGroomer.objects.filter(groomer=groomer, dia_semana=dia_modelo).first()
    if not disp:
        return JsonResponse({'slots': []})

    slots = []
    current = datetime.combine(fecha, disp.hora_inicio)
    end_time = datetime.combine(fecha, disp.hora_fin)
    duracion = timedelta(minutes=calcular_duracion(servicio, 'mediano'))

    while current + duracion <= end_time:
        fin_slot = current + duracion
        errores = validar_slot_disponible(groomer,
            timezone.make_aware(current), timezone.make_aware(fin_slot))
        if not errores:
            slots.append(current.strftime('%H:%M'))
        current += timedelta(minutes=15)

    return JsonResponse({'slots': slots})
