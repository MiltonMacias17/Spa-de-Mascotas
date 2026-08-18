from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from apps.usuarios.decorators import login_requerido, requiere_rol
from .models import Mascota, Cliente, MascotaDueno, HistorialMascota, Vacuna
from .forms import FormMascota, FormVacuna


@login_requerido
def lista_mascotas(request):
    if request.user.es_cliente():
        try:
            cliente = request.user.cliente
            mascotas = cliente.mascotas.filter(activa=True)
        except Cliente.DoesNotExist:
            mascotas = Mascota.objects.none()
    else:
        mascotas = Mascota.objects.filter(activa=True).select_related()

    return render(request, 'mascotas/lista.html', {'mascotas': mascotas})


@login_requerido
def detalle_mascota(request, pk):
    mascota = get_object_or_404(Mascota, pk=pk, activa=True)
    if request.user.es_cliente():
        try:
            cliente = request.user.cliente
            if not mascota.duenos.filter(pk=cliente.pk).exists():
                messages.error(request, 'No tienes permiso para ver esta mascota.')
                return redirect('mascotas:lista')
        except Cliente.DoesNotExist:
            return redirect('mascotas:lista')

    historial = mascota.historial.all()[:20]
    vacunas   = mascota.vacunas.all()
    citas     = mascota.citas.order_by('-fecha_hora_inicio')[:10]
    return render(request, 'mascotas/detalle.html', {
        'mascota': mascota,
        'historial': historial,
        'vacunas': vacunas,
        'citas': citas,
    })


@login_requerido
def nueva_mascota(request):
    if request.method == 'POST':
        form = FormMascota(request.POST, request.FILES)
        if form.is_valid():
            mascota = form.save()
            # asociar al cliente si es cliente
            if request.user.es_cliente():
                try:
                    MascotaDueno.objects.create(
                        mascota=mascota,
                        cliente=request.user.cliente,
                        es_dueno_principal=True,
                    )
                except Exception:
                    pass
            HistorialMascota.objects.create(
                mascota=mascota,
                tipo_evento='servicio',
                descripcion='Mascota registrada en el sistema.',
                creado_por=request.user,
            )
            messages.success(request, f'Mascota "{mascota.nombre}" registrada exitosamente.')
            return redirect('mascotas:detalle', pk=mascota.pk)
    else:
        form = FormMascota()
    return render(request, 'mascotas/formulario.html', {'form': form, 'titulo': 'Nueva Mascota'})


@login_requerido
def editar_mascota(request, pk):
    mascota = get_object_or_404(Mascota, pk=pk)
    if request.method == 'POST':
        form = FormMascota(request.POST, request.FILES, instance=mascota)
        if form.is_valid():
            form.save()
            messages.success(request, 'Datos actualizados correctamente.')
            return redirect('mascotas:detalle', pk=mascota.pk)
    else:
        form = FormMascota(instance=mascota)
    return render(request, 'mascotas/formulario.html', {'form': form, 'titulo': 'Editar Mascota', 'mascota': mascota})


@login_requerido
@requiere_rol('admin', 'recepcion')
def eliminar_mascota(request, pk):
    mascota = get_object_or_404(Mascota, pk=pk)
    mascota.activa = False
    mascota.save(update_fields=['activa'])
    messages.success(request, f'Mascota "{mascota.nombre}" desactivada.')
    return redirect('mascotas:lista')


@login_requerido
def historial_mascota(request, pk):
    mascota  = get_object_or_404(Mascota, pk=pk, activa=True)
    historial = mascota.historial.all()
    return render(request, 'mascotas/historial.html', {'mascota': mascota, 'historial': historial})
