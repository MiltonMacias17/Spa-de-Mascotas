from functools import wraps
from django.shortcuts import redirect, render
from django.contrib import messages


def login_requerido(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, 'Debes iniciar sesión para acceder a esta página.')
            return redirect('usuarios:login')
        return view_func(request, *args, **kwargs)
    return wrapper


def requiere_rol(*roles):
    """
    Uso: @requiere_rol('admin', 'recepcion')
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('usuarios:login')
            if not request.user.rol or request.user.rol.nombre not in roles:
                return render(request, '403.html', status=403)
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def solo_admin(view_func):
    return requiere_rol('admin')(view_func)


def solo_personal(view_func):
    return requiere_rol('admin', 'recepcion', 'groomer')(view_func)


def no_clientes(view_func):
    return requiere_rol('admin', 'recepcion')(view_func)
