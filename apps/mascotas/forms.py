from django import forms
from .models import Mascota, Vacuna


class FormMascota(forms.ModelForm):
    class Meta:
        model = Mascota
        fields = ['nombre', 'especie', 'raza', 'tamanio', 'fecha_nacimiento',
                  'alergias', 'temperamento', 'peso_kg', 'restricciones', 'foto_perfil']
        widgets = {
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date'}),
            'alergias':         forms.Textarea(attrs={'rows': 3}),
            'restricciones':    forms.Textarea(attrs={'rows': 3}),
        }


class FormVacuna(forms.ModelForm):
    class Meta:
        model = Vacuna
        fields = ['nombre', 'fecha_aplicacion', 'fecha_vencimiento', 'veterinario', 'documento']
        widgets = {
            'fecha_aplicacion':  forms.DateInput(attrs={'type': 'date'}),
            'fecha_vencimiento': forms.DateInput(attrs={'type': 'date'}),
        }
