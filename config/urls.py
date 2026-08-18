from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', lambda r: redirect('usuarios:login'), name='home'),
    path('auth/', include('apps.usuarios.urls', namespace='usuarios')),
    path('dashboard/', include('apps.reportes.urls', namespace='dashboard')),
    path('mascotas/', include('apps.mascotas.urls', namespace='mascotas')),
    path('agenda/', include('apps.agenda.urls', namespace='agenda')),
    path('grooming/', include('apps.grooming.urls', namespace='grooming')),
    path('inventario/', include('apps.inventario.urls', namespace='inventario')),
    path('tienda/', include('apps.tienda.urls', namespace='tienda')),
    path('facturacion/', include('apps.facturacion.urls', namespace='facturacion')),
    path('notificaciones/', include('apps.notificaciones.urls', namespace='notificaciones')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
