from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from apps.usuarios.decorators import login_requerido, requiere_rol, no_clientes
from .models import Factura, DetalleFactura, Pago
from apps.agenda.models import Cita
from apps.mascotas.models import Cliente


@login_requerido
def lista_facturas(request):
    if request.user.es_cliente():
        try:
            facturas = Factura.objects.filter(cliente=request.user.cliente)
        except Exception:
            facturas = Factura.objects.none()
    else:
        facturas = Factura.objects.all().select_related('cliente')
    return render(request, 'facturacion/lista.html', {'facturas': facturas})


@login_requerido
def detalle_factura(request, pk):
    factura = get_object_or_404(Factura, pk=pk)
    if request.user.es_cliente():
        try:
            if factura.cliente != request.user.cliente:
                messages.error(request, 'No tienes permiso.')
                return redirect('facturacion:lista')
        except Exception:
            return redirect('facturacion:lista')
    return render(request, 'facturacion/detalle.html', {'factura': factura})


@login_requerido
@no_clientes
def crear_factura_cita(request, cita_id):
    cita = get_object_or_404(Cita, pk=cita_id, estado='completada')
    if Factura.objects.filter(cita=cita).exists():
        messages.warning(request, 'Esta cita ya tiene una factura.')
        return redirect('agenda:detalle_cita', pk=cita_id)

    dueno = cita.mascota.mascotadueno_set.filter(es_dueno_principal=True).first()
    if not dueno:
        messages.error(request, 'No se encontró cliente dueño de la mascota.')
        return redirect('agenda:detalle_cita', pk=cita_id)

    if request.method == 'POST':
        metodo = request.POST.get('metodo_pago', 'efectivo')
        factura = Factura.objects.create(
            cita=cita,
            cliente=dueno.cliente,
            subtotal=cita.precio_calculado,
            impuesto=0,
            total=cita.precio_calculado,
            metodo_pago=metodo,
            estado='pagada',
        )
        DetalleFactura.objects.create(
            factura=factura,
            descripcion=f'{cita.servicio.nombre} — {cita.mascota.nombre}',
            cantidad=1,
            precio_unitario=cita.precio_calculado,
        )
        Pago.objects.create(
            factura=factura,
            monto=cita.precio_calculado,
            estado='completado',
        )
        messages.success(request, f'Factura #{factura.pk} generada.')
        return redirect('facturacion:detalle', pk=factura.pk)

    return render(request, 'facturacion/crear.html', {'cita': cita, 'cliente': dueno.cliente})
