from django.urls import path
from . import views

app_name = 'grooming'

urlpatterns = [
    path('ficha/<int:pk>/', views.ficha_grooming, name='ficha'),
    path('ficha/<int:pk>/checklist/', views.actualizar_checklist, name='checklist'),
    path('ficha/<int:pk>/fotos/', views.subir_fotos, name='fotos'),
    path('ficha/<int:pk>/cerrar/', views.cerrar_ficha, name='cerrar'),
]
