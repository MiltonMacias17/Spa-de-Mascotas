from django.shortcuts import render
from apps.usuarios.decorators import login_requerido
from .models import Notificacion


@login_requerido
def mis_notificaciones(request):
    notifs = Notificacion.objects.filter(destinatario=request.user).order_by('-fecha_programacion')[:50]
    return render(request, 'notificaciones/lista.html', {'notificaciones': notifs})
