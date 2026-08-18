from django.shortcuts import render, redirect
from django.utils import timezone
from django.db.models import Count, Sum, Avg
from apps.usuarios.decorators import login_requerido
from datetime import timedelta


@login_requerido
def dashboard(request):
    user = request.user
    if user.es_admin() or user.es_recepcion():
        return dashboard_admin(request)
    elif user.es_groomer():
        return dashboard_groomer(request)
    elif user.es_cliente():
        return dashboard_cliente(request)
    return redirect('usuarios:login')


def dashboard_admin(request):
    from apps.agenda.models import Cita
    from apps.inventario.models import Producto
    from apps.mascotas.models import Mascota, Cliente
    from apps.facturacion.models import Factura

    hoy = timezone.now().date()
    inicio_semana = hoy - timedelta(days=hoy.weekday())

    citas_hoy       = Cita.objects.filter(fecha_hora_inicio__date=hoy).count()
    citas_semana    = Cita.objects.filter(fecha_hora_inicio__date__gte=inicio_semana).count()
    ingresos_hoy    = Factura.objects.filter(
        fecha_emision__date=hoy, estado='pagada'
    ).aggregate(total=Sum('total'))['total'] or 0
    total_mascotas  = Mascota.objects.filter(activa=True).count()
    total_clientes  = Cliente.objects.count()
    bajo_stock      = Producto.objects.filter(activo=True).count()

    citas_pendientes = Cita.objects.filter(
        estado='agendada',
        fecha_hora_inicio__date=hoy,
    ).select_related('mascota', 'groomer', 'servicio').order_by('fecha_hora_inicio')

    productos_criticos = [p for p in Producto.objects.filter(activo=True) if p.bajo_stock()]

    return render(request, 'dashboard/admin.html', {
        'citas_hoy': citas_hoy,
        'citas_semana': citas_semana,
        'ingresos_hoy': ingresos_hoy,
        'total_mascotas': total_mascotas,
        'total_clientes': total_clientes,
        'citas_pendientes': citas_pendientes,
        'productos_criticos': productos_criticos,
    })


def dashboard_groomer(request):
    from apps.agenda.models import Cita, Groomer
    hoy = timezone.now().date()
    try:
        groomer = request.user.groomer
        citas_hoy = Cita.objects.filter(
            groomer=groomer,
            fecha_hora_inicio__date=hoy,
            estado__in=['agendada', 'confirmada', 'en_progreso'],
        ).select_related('mascota', 'servicio').order_by('fecha_hora_inicio')
        citas_completadas_hoy = Cita.objects.filter(
            groomer=groomer,
            fecha_hora_inicio__date=hoy,
            estado='completada',
        ).count()
    except Exception:
        citas_hoy = []
        citas_completadas_hoy = 0

    return render(request, 'dashboard/groomer.html', {
        'citas_hoy': citas_hoy,
        'citas_completadas_hoy': citas_completadas_hoy,
        'hoy': hoy,
    })


def dashboard_cliente(request):
    from apps.mascotas.models import Cliente
    from apps.agenda.models import Cita
    try:
        cliente   = request.user.cliente
        mascotas  = cliente.mascotas.filter(activa=True)
        proximas  = Cita.objects.filter(
            mascota__in=mascotas,
            estado__in=['agendada', 'confirmada'],
            fecha_hora_inicio__gte=timezone.now(),
        ).select_related('mascota', 'servicio', 'groomer').order_by('fecha_hora_inicio')[:5]
    except Exception:
        mascotas = []
        proximas = []

    return render(request, 'dashboard/cliente.html', {
        'mascotas': mascotas,
        'proximas_citas': proximas,
    })


@login_requerido
def reporte_ocupacion(request):
    from apps.agenda.models import Cita, Groomer
    from collections import defaultdict

    dias = int(request.GET.get('dias', 7))
    fecha_inicio = timezone.now().date() - timedelta(days=dias)

    citas = Cita.objects.filter(
        fecha_hora_inicio__date__gte=fecha_inicio,
    ).select_related('groomer', 'servicio')

    por_groomer = defaultdict(int)
    por_dia     = defaultdict(int)
    por_servicio = defaultdict(int)

    for cita in citas:
        por_groomer[str(cita.groomer)] += 1
        por_dia[str(cita.fecha_hora_inicio.date())] += 1
        por_servicio[cita.servicio.nombre] += 1

    return render(request, 'reportes/ocupacion.html', {
        'por_groomer': dict(por_groomer),
        'por_dia': dict(sorted(por_dia.items())),
        'por_servicio': dict(sorted(por_servicio.items(), key=lambda x: -x[1])),
        'dias': dias,
    })
