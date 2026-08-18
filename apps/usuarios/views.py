from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.utils import timezone
from .models import Usuario, Rol
from .forms import FormRegistro, FormLogin, FormCambiarPassword, FormRecuperarPassword
from .utils import (enviar_email_activacion, enviar_email_recuperacion,
                    registrar_log, validar_password_seguro)
from .decorators import login_requerido, solo_admin
import pyotp


def vista_login(request):
    if request.user.is_authenticated:
        return redirect('dashboard:inicio')

    if request.method == 'POST':
        form = FormLogin(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            try:
                user = Usuario.objects.get(email=email)
            except Usuario.DoesNotExist:
                messages.error(request, 'Credenciales incorrectas.')
                return render(request, 'usuarios/login.html', {'form': form})

            if user.esta_bloqueado():
                minutos = int((user.bloqueado_hasta - timezone.now()).total_seconds() / 60) + 1
                messages.error(request, f'Cuenta bloqueada. Intenta en {minutos} minuto(s).')
                return render(request, 'usuarios/login.html', {'form': form})

            auth_user = authenticate(request, username=user.email, password=password)
            if auth_user is None:
                user.registrar_intento_fallido()
                restantes = 5 - user.intentos_fallidos
                if restantes > 0:
                    messages.error(request, f'Contraseña incorrecta. Te quedan {restantes} intento(s).')
                else:
                    messages.error(request, 'Cuenta bloqueada por 15 minutos.')
                registrar_log(user, 'login_fallido', request)
                return render(request, 'usuarios/login.html', {'form': form})

            if not auth_user.email_verificado:
                messages.warning(request, 'Debes verificar tu correo antes de iniciar sesión.')
                return render(request, 'usuarios/login.html', {'form': form})

            # 2FA para admin
            if auth_user.two_factor_activo and auth_user.es_admin():
                request.session['_2fa_user_id'] = auth_user.pk
                return redirect('usuarios:verificar_2fa')

            auth_user.limpiar_intentos()
            login(request, auth_user)
            registrar_log(auth_user, 'login_exitoso', request)
            messages.success(request, f'Bienvenido/a, {auth_user.first_name or auth_user.email}!')
            return redirect('dashboard:inicio')
    else:
        form = FormLogin()

    return render(request, 'usuarios/login.html', {'form': form})


def vista_logout(request):
    if request.user.is_authenticated:
        registrar_log(request.user, 'logout', request)
        logout(request)
    messages.info(request, 'Sesión cerrada correctamente.')
    return redirect('usuarios:login')


def vista_registro(request):
    if request.user.is_authenticated:
        return redirect('dashboard:inicio')

    if request.method == 'POST':
        form = FormRegistro(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = form.cleaned_data['email'].split('@')[0] + str(Usuario.objects.count())
            user.set_password(form.cleaned_data['password1'])
            user.email_verificado = False
            try:
                rol_cliente = Rol.objects.get(nombre='cliente')
                user.rol = rol_cliente
            except Rol.DoesNotExist:
                pass
            user.save()

            # Crear perfil de cliente
            from apps.mascotas.models import Cliente
            Cliente.objects.create(
                usuario=user,
                nombre=form.cleaned_data.get('nombre', ''),
                ci=form.cleaned_data.get('ci', ''),
                telefono=form.cleaned_data.get('telefono', ''),
            )

            enviar_email_activacion(user, request)
            registrar_log(user, 'registro', request)
            messages.success(request, 'Cuenta creada. Revisa tu correo para activarla.')
            return redirect('usuarios:login')
    else:
        form = FormRegistro()

    return render(request, 'usuarios/registro.html', {'form': form})


def activar_cuenta(request, token):
    try:
        user = Usuario.objects.get(token_activacion=token)
    except Usuario.DoesNotExist:
        messages.error(request, 'Token inválido.')
        return redirect('usuarios:login')

    if not user.token_valido():
        messages.error(request, 'El enlace expiró. Solicita uno nuevo.')
        return redirect('usuarios:login')

    user.email_verificado = True
    user.is_active = True
    user.token_activacion = ''
    user.token_expiracion = None
    user.save(update_fields=['email_verificado', 'is_active', 'token_activacion', 'token_expiracion'])
    registrar_log(user, 'activacion_cuenta', request)
    messages.success(request, '¡Cuenta activada! Ya puedes iniciar sesión.')
    return redirect('usuarios:login')


def recuperar_password(request):
    if request.method == 'POST':
        form = FormRecuperarPassword(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = Usuario.objects.get(email=email)
                enviar_email_recuperacion(user, request)
            except Usuario.DoesNotExist:
                pass
            messages.success(request, 'Si el correo existe, recibirás un enlace de recuperación.')
            return redirect('usuarios:login')
    else:
        form = FormRecuperarPassword()
    return render(request, 'usuarios/recuperar_password.html', {'form': form})


def reset_password(request, token):
    try:
        user = Usuario.objects.get(token_activacion=token)
    except Usuario.DoesNotExist:
        messages.error(request, 'Token inválido o expirado.')
        return redirect('usuarios:login')

    if not user.token_valido():
        messages.error(request, 'El enlace expiró. Solicita uno nuevo.')
        return redirect('usuarios:recuperar_password')

    if request.method == 'POST':
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')
        errores = validar_password_seguro(password1)
        if errores:
            for e in errores:
                messages.error(request, e)
        elif password1 != password2:
            messages.error(request, 'Las contraseñas no coinciden.')
        else:
            user.set_password(password1)
            user.token_activacion = ''
            user.token_expiracion = None
            user.save()
            registrar_log(user, 'reset_password', request)
            messages.success(request, 'Contraseña actualizada. Ya puedes iniciar sesión.')
            return redirect('usuarios:login')

    return render(request, 'usuarios/reset_password.html', {'token': token})


def verificar_2fa(request):
    user_id = request.session.get('_2fa_user_id')
    if not user_id:
        return redirect('usuarios:login')

    user = get_object_or_404(Usuario, pk=user_id)

    if request.method == 'POST':
        codigo = request.POST.get('codigo', '').strip()
        totp = pyotp.TOTP(user.two_factor_secret)
        if totp.verify(codigo):
            user.limpiar_intentos()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            del request.session['_2fa_user_id']
            registrar_log(user, 'login_2fa_exitoso', request)
            messages.success(request, f'Bienvenido/a, {user.first_name or user.email}!')
            return redirect('dashboard:inicio')
        else:
            messages.error(request, 'Código 2FA incorrecto.')

    return render(request, 'usuarios/verificar_2fa.html')


@login_requerido
def perfil(request):
    return render(request, 'usuarios/perfil.html', {'usuario': request.user})


@login_requerido
@solo_admin
def setup_2fa(request):
    user = request.user
    if not user.two_factor_secret:
        user.two_factor_secret = pyotp.random_base32()
        user.save(update_fields=['two_factor_secret'])

    totp = pyotp.TOTP(user.two_factor_secret)
    uri = totp.provisioning_uri(user.email, issuer_name='Pet Spa')

    if request.method == 'POST':
        codigo = request.POST.get('codigo', '').strip()
        if totp.verify(codigo):
            user.two_factor_activo = True
            user.save(update_fields=['two_factor_activo'])
            messages.success(request, '2FA activado correctamente.')
            return redirect('usuarios:perfil')
        else:
            messages.error(request, 'Código incorrecto. Intenta de nuevo.')

    return render(request, 'usuarios/setup_2fa.html', {'uri': uri, 'secret': user.two_factor_secret})
