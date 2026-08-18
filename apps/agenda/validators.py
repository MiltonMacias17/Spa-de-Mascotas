from django.utils import timezone
from .models import Cita, DisponibilidadGroomer, BloqueoCalendario


def calcular_duracion(servicio, tamanio_mascota):
    factores = {'pequeno': 1.0, 'mediano': 1.10, 'grande': 1.15, 'gigante': 1.30}
    factor = factores.get(tamanio_mascota, 1.0)
    return int(servicio.duracion_base_minutos * factor)


def validar_slot_disponible(groomer, fecha_inicio, fecha_fin, excluir_cita_id=None):
    errores = []

    # Verificar bloqueos de calendario
    bloqueos = BloqueoCalendario.objects.filter(
        fecha_inicio__lt=fecha_fin,
        fecha_fin__gt=fecha_inicio,
    ).filter(
        groomer=None
    ) | BloqueoCalendario.objects.filter(
        fecha_inicio__lt=fecha_fin,
        fecha_fin__gt=fecha_inicio,
        groomer=groomer,
    )
    if bloqueos.exists():
        errores.append(f'El horario seleccionado tiene un bloqueo: {bloqueos.first().get_tipo_display()}.')

    # Verificar solapamiento con otras citas
    citas_qs = Cita.objects.filter(
        groomer=groomer,
        estado__in=['agendada', 'confirmada', 'en_progreso'],
        fecha_hora_inicio__lt=fecha_fin,
        fecha_hora_fin__gt=fecha_inicio,
    )
    if excluir_cita_id:
        citas_qs = citas_qs.exclude(pk=excluir_cita_id)

    if citas_qs.count() >= groomer.capacidad_simultanea:
        errores.append('El groomer ya tiene una cita en ese horario.')

    # Verificar horario laboral
    dia_semana = fecha_inicio.weekday()
    # Django: Monday=0, Sunday=6. Nuestro modelo: 0=Dom, 1=Lun
    dia_modelo = (dia_semana + 1) % 7
    disponibilidad = DisponibilidadGroomer.objects.filter(
        groomer=groomer,
        dia_semana=dia_modelo,
    ).first()
    if disponibilidad:
        hora_inicio_disp = disponibilidad.hora_inicio
        hora_fin_disp = disponibilidad.hora_fin
        if fecha_inicio.time() < hora_inicio_disp or fecha_fin.time() > hora_fin_disp:
            errores.append(f'Fuera del horario laboral del groomer ({hora_inicio_disp}-{hora_fin_disp}).')

    return errores
