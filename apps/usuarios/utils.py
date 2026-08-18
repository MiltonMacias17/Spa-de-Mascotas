import re
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from apps.usuarios.models import LogAuditoria


def validar_password_seguro(password):
    errores = []
    if len(password) < 8:
        errores.append('Mínimo 8 caracteres.')
    if not re.search(r'[A-Z]', password):
        errores.append('Debe incluir al menos una mayúscula.')
    if not re.search(r'[a-z]', password):
        errores.append('Debe incluir al menos una minúscula.')
    if not re.search(r'\d', password):
        errores.append('Debe incluir al menos un número.')
    if not re.search(r'[!@#$%^&*()_+\-=\[\]{};:\'",.<>?/\\|`~]', password):
        errores.append('Debe incluir al menos un símbolo (!@#$%...).')
    return errores


def calcular_fuerza_password(password):
    score = 0
    if len(password) >= 8:
        score += 1
    if len(password) >= 12:
        score += 1
    if re.search(r'[A-Z]', password):
        score += 1
    if re.search(r'[a-z]', password):
        score += 1
    if re.search(r'\d', password):
        score += 1
    if re.search(r'[!@#$%^&*()_+\-=\[\]{}]', password):
        score += 1
    if score <= 2:
        return 'debil'
    elif score <= 4:
        return 'media'
    else:
        return 'fuerte'


def enviar_email_activacion(usuario, request):
    token = usuario.generar_token_activacion()
    link = request.build_absolute_uri(f'/auth/activar/{token}/')
    asunto = 'Activa tu cuenta en Pet Spa'
    mensaje = f"""
Hola {usuario.first_name or usuario.email},

Gracias por registrarte en Pet Spa. Haz clic en el siguiente enlace para activar tu cuenta:

{link}

Este enlace es válido por 15 minutos.

Si no solicitaste esta cuenta, ignora este mensaje.

— Equipo Pet Spa
"""
    send_mail(
        subject=asunto,
        message=mensaje,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[usuario.email],
        fail_silently=True,
    )


def enviar_email_recuperacion(usuario, request):
    token = usuario.generar_token_activacion()
    link = request.build_absolute_uri(f'/auth/reset/{token}/')
    asunto = 'Recuperación de contraseña — Pet Spa'
    mensaje = f"""
Hola {usuario.first_name or usuario.email},

Recibimos una solicitud para restablecer tu contraseña.

Haz clic aquí para crear una nueva contraseña:
{link}

Este enlace es válido por 15 minutos.

Si no solicitaste esto, ignora este mensaje.

— Equipo Pet Spa
"""
    send_mail(
        subject=asunto,
        message=mensaje,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[usuario.email],
        fail_silently=True,
    )


def registrar_log(usuario, accion, request=None, detalle=''):
    ip = None
    ua = ''
    if request:
        ip = get_client_ip(request)
        ua = request.META.get('HTTP_USER_AGENT', '')
    LogAuditoria.objects.create(
        usuario=usuario,
        accion=accion,
        detalle=detalle,
        ip_address=ip,
        user_agent=ua,
    )


def get_client_ip(request):
    x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded:
        return x_forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '127.0.0.1')
