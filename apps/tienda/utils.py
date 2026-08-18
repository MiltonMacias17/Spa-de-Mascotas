import urllib.parse


def generar_link_whatsapp(carrito, telefono_tienda=''):
    lineas = ['🐾 *Pedido Pet Spa*\n']
    for item in carrito.items.all():
        nombre = item.producto.nombre
        if item.variante:
            nombre += f' ({item.variante.atributo}: {item.variante.valor})'
        lineas.append(f'• {nombre} x{item.cantidad} — Bs. {item.subtotal():.2f}')
    lineas.append(f'\n*Total: Bs. {carrito.total():.2f}*')
    lineas.append('\nPor favor confirmar disponibilidad y método de pago. ¡Gracias!')
    mensaje = '\n'.join(lineas)
    encoded = urllib.parse.quote(mensaje)
    if telefono_tienda:
        return f'https://wa.me/{telefono_tienda}?text={encoded}'
    return f'https://wa.me/?text={encoded}'


def generar_link_telegram(carrito):
    lineas = ['🐾 Pedido Pet Spa\n']
    for item in carrito.items.all():
        nombre = item.producto.nombre
        if item.variante:
            nombre += f' ({item.variante.atributo}: {item.variante.valor})'
        lineas.append(f'• {nombre} x{item.cantidad} - Bs. {item.subtotal():.2f}')
    lineas.append(f'\nTotal: Bs. {carrito.total():.2f}')
    mensaje = '\n'.join(lineas)
    encoded = urllib.parse.quote(mensaje)
    return f'https://t.me/share/url?url=&text={encoded}'
