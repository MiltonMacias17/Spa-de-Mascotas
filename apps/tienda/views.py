from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from apps.usuarios.decorators import login_requerido
from apps.inventario.models import Producto, Categoria
from .models import Carrito, DetalleCarrito, Pedido, DetallePedido
from .utils import generar_link_whatsapp, generar_link_telegram
import secrets


def get_or_create_carrito(request):
    token = request.session.get('carrito_token')
    if token:
        carrito = Carrito.objects.filter(session_token=token, expires_at__gt=timezone.now()).first()
        if carrito:
            return carrito
    carrito = Carrito.objects.create(
        usuario=request.user if request.user.is_authenticated else None,
        session_token=secrets.token_urlsafe(32),
        expires_at=timezone.now() + timezone.timedelta(days=7),
    )
    request.session['carrito_token'] = carrito.session_token
    return carrito


def catalogo(request):
    categoria_id = request.GET.get('categoria')
    busqueda     = request.GET.get('q', '')
    productos    = Producto.objects.filter(activo=True, es_insumo=False).select_related('categoria')

    if categoria_id:
        productos = productos.filter(categoria_id=categoria_id)
    if busqueda:
        productos = productos.filter(nombre__icontains=busqueda)

    categorias = Categoria.objects.filter(padre=None)
    carrito    = get_or_create_carrito(request)

    return render(request, 'tienda/catalogo.html', {
        'productos': productos,
        'categorias': categorias,
        'busqueda': busqueda,
        'carrito_count': carrito.cantidad_items(),
    })


def detalle_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk, activo=True)
    variantes = producto.variantes.all()
    carrito   = get_or_create_carrito(request)
    return render(request, 'tienda/producto.html', {
        'producto': producto,
        'variantes': variantes,
        'carrito_count': carrito.cantidad_items(),
    })


def ver_carrito(request):
    carrito = get_or_create_carrito(request)
    return render(request, 'tienda/carrito.html', {
        'carrito': carrito,
        'items': carrito.items.select_related('producto', 'variante').all(),
    })


def agregar_al_carrito(request):
    if request.method != 'POST':
        return JsonResponse({'ok': False})

    producto_id = request.POST.get('producto_id')
    variante_id = request.POST.get('variante_id')
    cantidad    = int(request.POST.get('cantidad', 1))

    producto = get_object_or_404(Producto, pk=producto_id, activo=True)
    variante = None
    if variante_id:
        from apps.inventario.models import VarianteProducto
        variante = VarianteProducto.objects.filter(pk=variante_id).first()

    precio = float(producto.precio_base)
    if variante:
        precio += float(variante.precio_extra)

    carrito = get_or_create_carrito(request)
    item, created = DetalleCarrito.objects.get_or_create(
        carrito=carrito,
        producto=producto,
        variante=variante,
        defaults={'cantidad': cantidad, 'precio_unitario': precio},
    )
    if not created:
        item.cantidad += cantidad
        item.save(update_fields=['cantidad'])

    return JsonResponse({
        'ok': True,
        'total_items': carrito.cantidad_items(),
        'mensaje': f'{producto.nombre} agregado al carrito.',
    })


def quitar_del_carrito(request, item_id):
    carrito = get_or_create_carrito(request)
    DetalleCarrito.objects.filter(pk=item_id, carrito=carrito).delete()
    messages.success(request, 'Producto eliminado del carrito.')
    return redirect('tienda:carrito')


def pedido_whatsapp(request):
    carrito = get_or_create_carrito(request)
    if not carrito.items.exists():
        messages.warning(request, 'El carrito está vacío.')
        return redirect('tienda:catalogo')

    link_wa = generar_link_whatsapp(carrito)
    link_tg = generar_link_telegram(carrito)

    # Guardar pedido si el usuario está autenticado
    if request.user.is_authenticated:
        try:
            from apps.mascotas.models import Cliente
            cliente = request.user.cliente
            pedido  = Pedido.objects.create(
                carrito=carrito,
                cliente=cliente,
                subtotal=carrito.total(),
                total=carrito.total(),
                metodo_contacto='whatsapp',
            )
            for item in carrito.items.all():
                DetallePedido.objects.create(
                    pedido=pedido,
                    producto=item.producto,
                    cantidad=item.cantidad,
                    precio_unitario=item.precio_unitario,
                )
        except Exception:
            pass

    return render(request, 'tienda/pedido_whatsapp.html', {
        'carrito': carrito,
        'link_wa': link_wa,
        'link_tg': link_tg,
    })
