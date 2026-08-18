from django import forms
from .models import Cita, BloqueoCalendario, DisponibilidadGroomer


class FormCita(forms.ModelForm):
    class Meta:
        model = Cita
        fields = ['mascota', 'groomer', 'servicio', 'fecha_hora_inicio', 'notas']
        widgets = {
            'fecha_hora_inicio': forms.DateTimeInput(
                attrs={'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M',
            ),
            'notas': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['fecha_hora_inicio'].input_formats = ['%Y-%m-%dT%H:%M']


class FormBloqueo(forms.ModelForm):
    class Meta:
        model = BloqueoCalendario
        fields = ['tipo', 'fecha_inicio', 'fecha_fin', 'groomer', 'descripcion']
        widgets = {
            'fecha_inicio': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
            'fecha_fin':    forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
            'descripcion':  forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for f in ['fecha_inicio', 'fecha_fin']:
            self.fields[f].input_formats = ['%Y-%m-%dT%H:%M']


class FormDisponibilidad(forms.ModelForm):
    class Meta:
        model = DisponibilidadGroomer
        fields = ['groomer', 'dia_semana', 'hora_inicio', 'hora_fin', 'intervalo_descanso']
        widgets = {
            'hora_inicio': forms.TimeInput(attrs={'type': 'time'}),
            'hora_fin':    forms.TimeInput(attrs={'type': 'time'}),
        }
