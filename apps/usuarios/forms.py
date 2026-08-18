from django import forms
from .models import Usuario
from .utils import validar_password_seguro


class FormLogin(forms.Form):
    email    = forms.EmailField(label='Correo electrónico',
                   widget=forms.EmailInput(attrs={'placeholder': 'tu@correo.com', 'autofocus': True}))
    password = forms.CharField(label='Contraseña',
                   widget=forms.PasswordInput(attrs={'placeholder': '••••••••'}))


class FormRegistro(forms.ModelForm):
    nombre    = forms.CharField(max_length=100, label='Nombre completo')
    ci        = forms.CharField(max_length=20, label='Cédula de identidad')
    telefono  = forms.CharField(max_length=20, label='Teléfono', required=False)
    password1 = forms.CharField(label='Contraseña',
                    widget=forms.PasswordInput(attrs={'id': 'id_password1'}))
    password2 = forms.CharField(label='Confirmar contraseña',
                    widget=forms.PasswordInput())

    class Meta:
        model = Usuario
        fields = ['email']

    def clean_password1(self):
        pwd = self.cleaned_data.get('password1', '')
        errores = validar_password_seguro(pwd)
        if errores:
            raise forms.ValidationError(errores)
        return pwd

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get('password1')
        p2 = cleaned.get('password2')
        if p1 and p2 and p1 != p2:
            self.add_error('password2', 'Las contraseñas no coinciden.')
        return cleaned

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Usuario.objects.filter(email=email).exists():
            raise forms.ValidationError('Ya existe una cuenta con este correo.')
        return email


class FormCambiarPassword(forms.Form):
    password_actual = forms.CharField(label='Contraseña actual',
                          widget=forms.PasswordInput())
    password1       = forms.CharField(label='Nueva contraseña',
                          widget=forms.PasswordInput(attrs={'id': 'id_password1'}))
    password2       = forms.CharField(label='Confirmar nueva contraseña',
                          widget=forms.PasswordInput())

    def clean_password1(self):
        pwd = self.cleaned_data.get('password1', '')
        errores = validar_password_seguro(pwd)
        if errores:
            raise forms.ValidationError(errores)
        return pwd

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('password1') != cleaned.get('password2'):
            self.add_error('password2', 'Las contraseñas no coinciden.')
        return cleaned


class FormRecuperarPassword(forms.Form):
    email = forms.EmailField(label='Correo electrónico',
                widget=forms.EmailInput(attrs={'placeholder': 'tu@correo.com'}))
