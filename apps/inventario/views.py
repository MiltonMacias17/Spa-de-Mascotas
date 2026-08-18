from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from apps.usuarios.decorators import login_requerido, requiere_rol, solo_admin
from .models import Producto, Categoria, VarianteProducto, MovimientoInventario
from .forms import FormProducto, FormCategoria


@login_requerido
@requiere_rol('admin', 'recepcion')
def lista_productos(request):
    productos = Producto.objects.filter(activo=True).select_related('categoria').order_by('nombre')
    bajo_stock = [p for p in productos if p.bajo_stock()]
    return render(request, 'inventario/lista.html', {
        'productos': productos,
        'bajo_stock': bajo_stock,
    })


@login_requerido
@solo_admin
def nuevo_producto(request):
    if request.method == 'POST':
        form = FormProducto(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Producto creado.')
            return redirect('inventario:lista')
    else:
        form = FormProducto()
    return render(request, 'inventario/formulario.html', {'form': form, 'titulo': 'Nuevo Producto'})


@login_requerido
@solo_admin
def editar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        form = FormProducto(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            form.save()
            messages.success(request, 'Producto actualizado.')
            return redirect('inventario:lista')
    else:
        form = FormProducto(instance=producto)
    return render(request, 'inventario/formulario.html', {'form': form, 'titulo': 'Editar Producto', 'producto': producto})


@login_requerido
@solo_admin
def entrada_inventario(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        cantidad = int(request.POST.get('cantidad', 0))
        nota     = request.POST.get('nota', '')
        if cantidad > 0:
            stock_antes = producto.stock_actual
            producto.stock_actual += cantidad
            producto.save(update_fields=['stock_actual'])
            MovimientoInventario.objects.create(
                producto=producto,
                tipo='entrada',
                cantidad=cantidad,
                stock_tras=producto.stock_actual,
                nota=nota,
            )
            messages.success(request, f'Se agregaron {cantidad} unidades a {producto.nombre}.')
        return redirect('inventario:lista')
    return render(request, 'inventario/entrada.html', {'producto': producto})


@login_requerido
@requiere_rol('admin', 'recepcion')
def alertas_inventario(request):
    productos_criticos = Producto.objects.filter(activo=True).order_by('stock_actual')
    productos_criticos = [p for p in productos_criticos if p.bajo_stock()]
    return render(request, 'inventario/alertas.html', {'productos': productos_criticos})
