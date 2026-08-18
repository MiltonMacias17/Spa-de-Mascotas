# Arquitectura del Sistema Web — Pet Spa
**Proyecto:** Sistema de Gestión para Spa & Tienda de Mascotas  
**Stack:** Django 5 · SQLite · HTML5 · CSS3 · JavaScript (Vanilla)  
**Versión:** 1.0 | **Fecha:** 2026-06-02

---

## 1. Descripción General

Sistema web–móvil (PWA-ready) para gestionar servicios de grooming, agenda de citas, tienda de accesorios, historial de mascotas, notificaciones automáticas y reportes. Implementado con el patrón **MVT (Model–View–Template)** de Django sobre una base de datos SQLite.

---

## 2. Stack Tecnológico

| Capa | Tecnología | Propósito |
|---|---|---|
| Backend | Django 5.x | Framework principal, lógica de negocio, ORM |
| Base de datos | SQLite 3 | Almacenamiento relacional local |
| Frontend | HTML5 + CSS3 + JS (Vanilla) | Interfaces de usuario |
| Autenticación | Django Auth + PyJWT | Sesiones y tokens |
| 2FA | pyotp + qrcode | Google Authenticator para Admin |
| Contraseñas | bcrypt (via django-bcrypt) | Hashing seguro |
| Emails | Django send_mail / SMTP | Notificaciones y activación |
| CSS Framework | (Tailwind CSS o CSS propio) | Diseño responsivo |
| Servidor dev | Django runserver | Desarrollo local |
| Servidor prod | Gunicorn + Nginx | Despliegue opcional |

---

## 3. Patrón de Arquitectura — MVT

```
Navegador (Cliente)
       │
       ▼
  urls.py (Router)
       │
       ▼
  views.py (Controlador / Lógica)
    ├── Valida permisos RBAC
    ├── Llama al ORM (models.py)
    └── Devuelve Template (.html)
       │
       ▼
  models.py (ORM → SQLite)
       │
       ▼
  templates/*.html + static/*.css/*.js
```

**Flujo de una petición:**
1. El navegador hace `GET /citas/nueva/`
2. `urls.py` enruta a `citas/views.py → nueva_cita()`
3. La view verifica rol del usuario (RBAC)
4. Consulta `Groomer`, `Servicio`, `Disponibilidad` via ORM
5. Renderiza `templates/citas/nueva.html` con el contexto
6. El navegador recibe HTML + CSS + JS

---

## 4. Diseño de Carpetas del Proyecto

```
petspa/                                  ← raíz del proyecto Django
│
├── manage.py
├── requirements.txt
├── .env                                 ← variables de entorno (SECRET_KEY, etc.)
├── db.sqlite3                           ← base de datos SQLite
│
├── petspa/                              ← configuración global del proyecto
│   ├── __init__.py
│   ├── settings.py                      ← configuración Django
│   ├── urls.py                          ← router principal
│   ├── wsgi.py
│   └── asgi.py
│
├── apps/                                ← todas las aplicaciones Django
│   │
│   ├── usuarios/                        ← Módulo de Autenticación y Roles
│   │   ├── migrations/
│   │   ├── templates/
│   │   │   └── usuarios/
│   │   │       ├── login.html
│   │   │       ├── registro.html
│   │   │       ├── activar_cuenta.html
│   │   │       ├── perfil.html
│   │   │       ├── cambiar_password.html
│   │   │       ├── recuperar_password.html
│   │   │       └── setup_2fa.html
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py                    ← Usuario, Rol, SesionUsuario, LogAuditoria
│   │   ├── views.py                     ← login, registro, activacion, 2fa
│   │   ├── urls.py
│   │   ├── forms.py
│   │   ├── decorators.py                ← @requiere_rol('admin'), @login_requerido
│   │   └── utils.py                     ← generar_token, enviar_email_activacion
│   │
│   ├── mascotas/                        ← Módulo Clientes & Mascotas
│   │   ├── migrations/
│   │   ├── templates/
│   │   │   └── mascotas/
│   │   │       ├── lista.html
│   │   │       ├── detalle.html
│   │   │       ├── formulario.html
│   │   │       └── historial.html
│   │   ├── models.py                    ← Cliente, Mascota, HistorialMascota, Vacuna
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── forms.py
│   │
│   ├── agenda/                          ← Módulo de Agenda & Slots
│   │   ├── migrations/
│   │   ├── templates/
│   │   │   └── agenda/
│   │   │       ├── calendario.html
│   │   │       ├── nueva_cita.html
│   │   │       ├── detalle_cita.html
│   │   │       ├── reprogramar.html
│   │   │       └── bloqueos.html
│   │   ├── models.py                    ← Cita, DisponibilidadGroomer, BloqueoCalendario
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── forms.py
│   │   └── validators.py                ← validar_slot, validar_capacidad
│   │
│   ├── grooming/                        ← Módulo de Grooming
│   │   ├── migrations/
│   │   ├── templates/
│   │   │   └── grooming/
│   │   │       ├── ficha.html
│   │   │       ├── checklist.html
│   │   │       ├── fotos.html
│   │   │       └── cerrar_ficha.html
│   │   ├── models.py                    ← FichaGrooming, ChecklistItem, FotoServicio
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── forms.py
│   │
│   ├── inventario/                      ← Módulo de Inventario & Insumos
│   │   ├── migrations/
│   │   ├── templates/
│   │   │   └── inventario/
│   │   │       ├── lista.html
│   │   │       ├── entrada.html
│   │   │       ├── salida.html
│   │   │       └── alertas.html
│   │   ├── models.py                    ← Producto, Categoria, VarianteProducto, MovimientoInventario
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── signals.py                   ← alerta de bajo stock al guardar
│   │
│   ├── tienda/                          ← Módulo de Tienda & Carrito
│   │   ├── migrations/
│   │   ├── templates/
│   │   │   └── tienda/
│   │   │       ├── catalogo.html
│   │   │       ├── detalle_producto.html
│   │   │       ├── carrito.html
│   │   │       └── pedido_whatsapp.html
│   │   ├── models.py                    ← Carrito, DetalleCarrito, Pedido, DetallePedido
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── utils.py                     ← generar_mensaje_whatsapp()
│   │
│   ├── facturacion/                     ← Módulo de Pagos & Facturación
│   │   ├── migrations/
│   │   ├── templates/
│   │   │   └── facturacion/
│   │   │       ├── factura.html
│   │   │       ├── lista_facturas.html
│   │   │       └── recibo.html
│   │   ├── models.py                    ← Factura, DetalleFactura, Pago
│   │   ├── views.py
│   │   └── urls.py
│   │
│   ├── notificaciones/                  ← Módulo de Notificaciones
│   │   ├── migrations/
│   │   ├── models.py                    ← Notificacion, LogNotificacion
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── tasks.py                     ← jobs CRON: recordatorios 24h/2h
│   │
│   └── reportes/                        ← Módulo de Reportes
│       ├── templates/
│       │   └── reportes/
│       │       ├── dashboard.html
│       │       ├── ocupacion.html
│       │       ├── ventas.html
│       │       └── inventario_critico.html
│       ├── views.py
│       └── urls.py
│
├── static/                              ← archivos estáticos globales
│   ├── css/
│   │   ├── base.css                     ← estilos globales, variables CSS
│   │   ├── dashboard.css
│   │   ├── agenda.css
│   │   ├── formularios.css
│   │   └── responsive.css
│   ├── js/
│   │   ├── calendario.js                ← lógica de agenda drag & drop
│   │   ├── carrito.js                   ← gestión del carrito
│   │   ├── password_meter.js            ← medidor de fuerza de contraseña
│   │   ├── notificaciones.js            ← alertas en tiempo real
│   │   └── whatsapp.js                  ← generación de link de pedido
│   └── img/
│       └── logo.png
│
├── templates/                           ← templates globales
│   ├── base.html                        ← layout principal con navbar
│   ├── base_auth.html                   ← layout para páginas de login
│   ├── 403.html
│   ├── 404.html
│   └── 500.html
│
└── media/                               ← archivos subidos por usuarios
    └── mascotas/
        └── fotos/                       ← fotos antes/después del grooming
```

---

## 5. Diseño de la Base de Datos (Modelos Django)

### 5.1 Diagrama de Entidades Principales

```
┌──────────┐     ┌──────────┐     ┌───────────┐
│  roles   │◄────│ usuarios │────►│  clientes │
└──────────┘     └──────────┘     └───────────┘
                      │                  │
                      ▼                  ▼
               ┌──────────┐       ┌──────────┐
               │ groomers │       │ mascotas │
               └──────────┘       └──────────┘
                  │    │               │    │
                  ▼    ▼               ▼    ▼
            ┌──────┐ ┌──────┐   ┌──────┐ ┌──────────────┐
            │citas │ │disp. │   │citas │ │historial     │
            └──────┘ └──────┘   └──────┘ └──────────────┘
               │
      ┌────────┴────────┐
      ▼                 ▼
┌──────────┐     ┌────────────┐
│  ficha   │     │notificacion│
│ grooming │     └────────────┘
└──────────┘
      │
 ┌────┴─────┐
 ▼          ▼
checklist  fotos
```

### 5.2 Modelos por Aplicación

#### `usuarios/models.py`
```python
# Rol — Admin, Recepción, Groomer, Cliente
class Rol(models.Model):
    nombre      = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(blank=True)

# Usuario base del sistema (extiende AbstractBaseUser o AbstractUser)
class Usuario(AbstractUser):
    rol                = models.ForeignKey(Rol, on_delete=models.SET_NULL, null=True)
    telefono           = models.CharField(max_length=20, blank=True)
    esta_activo        = models.BooleanField(default=False)   # activo tras verificar email
    email_verificado   = models.BooleanField(default=False)
    token_activacion   = models.CharField(max_length=255, blank=True)
    token_expiracion   = models.DateTimeField(null=True)
    intentos_fallidos  = models.IntegerField(default=0)
    bloqueado_hasta    = models.DateTimeField(null=True)
    two_factor_secret  = models.CharField(max_length=32, blank=True)
    two_factor_activo  = models.BooleanField(default=False)
    ultimo_acceso      = models.DateTimeField(null=True)

# Sesión JWT del usuario
class SesionUsuario(models.Model):
    usuario         = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    token_jwt       = models.TextField()
    refresh_token   = models.CharField(max_length=255)
    ip_address      = models.GenericIPAddressField()
    user_agent      = models.TextField()
    fecha_expiracion = models.DateTimeField()
    creado_en       = models.DateTimeField(auto_now_add=True)

# Log de auditoría
class LogAuditoria(models.Model):
    usuario    = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True)
    accion     = models.CharField(max_length=255)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    fecha      = models.DateTimeField(auto_now_add=True)
```

#### `mascotas/models.py`
```python
class Cliente(models.Model):
    usuario    = models.OneToOneField(Usuario, on_delete=models.CASCADE)
    nombre     = models.CharField(max_length=100)
    ci         = models.CharField(max_length=20, unique=True)
    direccion  = models.TextField()
    canal_notificacion = models.CharField(max_length=20,
        choices=[('email','Email'),('whatsapp','WhatsApp'),('sms','SMS')])

class Mascota(models.Model):
    TAMANO = [('pequeño','Pequeño'),('mediano','Mediano'),
              ('grande','Grande'),('gigante','Gigante')]
    TEMPERAMENTO = [('tranquilo','Tranquilo'),('nervioso','Nervioso'),
                    ('agresivo','Agresivo'),('inquieto','Inquieto')]
    nombre             = models.CharField(max_length=100)
    especie            = models.CharField(max_length=50)
    raza               = models.CharField(max_length=100)
    tamanio            = models.CharField(max_length=20, choices=TAMANO)
    fecha_nacimiento   = models.DateField()
    alergias           = models.TextField(blank=True)
    temperamento       = models.CharField(max_length=20, choices=TEMPERAMENTO)
    peso_kg            = models.DecimalField(max_digits=5, decimal_places=2)
    restricciones      = models.TextField(blank=True)
    foto_perfil        = models.ImageField(upload_to='mascotas/perfil/', blank=True)

class MascotaDueno(models.Model):  # relación N:M mascota — cliente
    mascota = models.ForeignKey(Mascota, on_delete=models.CASCADE)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    es_dueno_principal = models.BooleanField(default=False)

class HistorialMascota(models.Model):
    TIPO = [('servicio','Servicio'),('recomendacion','Recomendación'),
            ('alerta','Alerta'),('cancelacion','Cancelación')]
    mascota     = models.ForeignKey(Mascota, on_delete=models.CASCADE)
    tipo_evento = models.CharField(max_length=30, choices=TIPO)
    descripcion = models.TextField()
    fecha       = models.DateTimeField(auto_now_add=True)
```

#### `agenda/models.py`
```python
class Servicio(models.Model):
    nombre                   = models.CharField(max_length=100)
    descripcion              = models.TextField()
    duracion_base_minutos    = models.IntegerField()   # múltiplo de 15
    precio_base              = models.DecimalField(max_digits=8, decimal_places=2)
    permite_doble_booking    = models.BooleanField(default=False)
    requiere_bloqueo_consecutivo = models.BooleanField(default=False)
    factor_tamanio_raza      = models.JSONField(default=dict)
    consumo_insumos          = models.JSONField(default=dict)

class Groomer(models.Model):
    usuario              = models.OneToOneField(Usuario, on_delete=models.CASCADE)
    especialidad         = models.CharField(max_length=100)
    capacidad_simultanea = models.IntegerField(default=1)
    horario_trabajo      = models.JSONField(default=dict)
    esta_activo          = models.BooleanField(default=True)

class DisponibilidadGroomer(models.Model):
    groomer            = models.ForeignKey(Groomer, on_delete=models.CASCADE)
    dia_semana         = models.IntegerField()  # 0=Dom … 6=Sab
    hora_inicio        = models.TimeField()
    hora_fin           = models.TimeField()
    intervalo_descanso = models.JSONField(default=dict)  # {"inicio":"12:30","fin":"14:00"}

class BloqueoCalendario(models.Model):
    TIPO = [('feriado','Feriado'),('mantenimiento','Mantenimiento'),
            ('vacaciones','Vacaciones'),('ausencia','Ausencia')]
    tipo            = models.CharField(max_length=20, choices=TIPO)
    fecha_inicio    = models.DateTimeField()
    fecha_fin       = models.DateTimeField()
    groomer         = models.ForeignKey(Groomer, null=True, blank=True,
                        on_delete=models.SET_NULL)  # NULL = bloqueo global
    descripcion     = models.TextField(blank=True)

class Cita(models.Model):
    ESTADO = [('agendada','Agendada'),('confirmada','Confirmada'),
              ('en_progreso','En Progreso'),('completada','Completada'),
              ('cancelada','Cancelada'),('no_asistio','No Asistió')]
    mascota           = models.ForeignKey(Mascota, on_delete=models.CASCADE)
    groomer           = models.ForeignKey(Groomer, on_delete=models.PROTECT)
    servicio          = models.ForeignKey(Servicio, on_delete=models.PROTECT)
    fecha_hora_inicio = models.DateTimeField()
    fecha_hora_fin    = models.DateTimeField()
    duracion_real     = models.IntegerField(null=True)
    estado            = models.CharField(max_length=20, choices=ESTADO,
                            default='agendada')
    creado_por        = models.ForeignKey(Usuario, on_delete=models.SET_NULL,
                            null=True, related_name='citas_creadas')
    reprogramado_por  = models.ForeignKey(Usuario, on_delete=models.SET_NULL,
                            null=True, related_name='citas_reprogramadas')
    fecha_reprogramacion = models.DateTimeField(null=True)
    notas             = models.TextField(blank=True)
    creado_en         = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['groomer','fecha_hora_inicio'],
                name='unique_groomer_slot'
            )
        ]
```

#### `grooming/models.py`
```python
class FichaGrooming(models.Model):
    cita               = models.OneToOneField(Cita, on_delete=models.CASCADE)
    raza_al_momento    = models.CharField(max_length=100)
    tamanio_al_momento = models.CharField(max_length=20)
    temperatura_animal = models.DecimalField(max_digits=4, decimal_places=1, null=True)
    estado_ingreso     = models.TextField()    # nudos, pulgas, heridas
    notas_internas     = models.TextField(blank=True)
    recomendaciones    = models.TextField(blank=True)
    consumido_inventario = models.BooleanField(default=False)
    fecha_cierre       = models.DateTimeField(null=True)

class ItemChecklistTemplate(models.Model):  # catálogo maestro de items
    nombre              = models.CharField(max_length=100)
    requiere_observacion = models.BooleanField(default=False)
    servicio            = models.ForeignKey(Servicio, on_delete=models.CASCADE,
                            null=True, blank=True)

class ChecklistItem(models.Model):  # instancia por ficha
    ficha        = models.ForeignKey(FichaGrooming, on_delete=models.CASCADE)
    item         = models.ForeignKey(ItemChecklistTemplate, on_delete=models.PROTECT)
    completado   = models.BooleanField(default=False)
    observacion  = models.TextField(blank=True)

    class Meta:
        unique_together = ('ficha', 'item')

class FotoServicio(models.Model):
    MOMENTO = [('antes','Antes'),('despues','Después')]
    ficha   = models.ForeignKey(FichaGrooming, on_delete=models.CASCADE)
    imagen  = models.ImageField(upload_to='mascotas/fotos/')
    momento = models.CharField(max_length=10, choices=MOMENTO)
    subida_en = models.DateTimeField(auto_now_add=True)
```

#### `inventario/models.py`
```python
class Categoria(models.Model):
    nombre = models.CharField(max_length=100)
    padre  = models.ForeignKey('self', null=True, blank=True,
                on_delete=models.SET_NULL)  # jerarquía árbol

class Producto(models.Model):
    nombre        = models.CharField(max_length=200)
    descripcion   = models.TextField()
    categoria     = models.ForeignKey(Categoria, on_delete=models.PROTECT)
    precio_base   = models.DecimalField(max_digits=8, decimal_places=2)
    stock_actual  = models.IntegerField(default=0)
    stock_minimo  = models.IntegerField(default=5)
    sku           = models.CharField(max_length=50, unique=True)
    imagen_url    = models.URLField(blank=True)
    es_insumo     = models.BooleanField(default=False)  # insumo de grooming vs producto tienda

class VarianteProducto(models.Model):
    producto     = models.ForeignKey(Producto, on_delete=models.CASCADE)
    atributo     = models.CharField(max_length=50)   # "talla", "fragancia"
    valor        = models.CharField(max_length=50)   # "1kg", "Lavanda"
    precio_extra = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    stock        = models.IntegerField(default=0)
    sku_variante = models.CharField(max_length=60, unique=True)
```

#### `tienda/models.py`
```python
class Carrito(models.Model):
    usuario       = models.ForeignKey(Usuario, null=True, blank=True,
                        on_delete=models.SET_NULL)
    session_token = models.CharField(max_length=64, unique=True)
    expires_at    = models.DateTimeField()  # 7 días
    creado_en     = models.DateTimeField(auto_now_add=True)

class DetalleCarrito(models.Model):
    carrito         = models.ForeignKey(Carrito, on_delete=models.CASCADE)
    producto        = models.ForeignKey(Producto, on_delete=models.PROTECT)
    variante        = models.ForeignKey(VarianteProducto, null=True,
                        blank=True, on_delete=models.SET_NULL)
    cantidad        = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=8, decimal_places=2)  # precio congelado

class Pedido(models.Model):
    ESTADO = [('pendiente','Pendiente'),('enviado','Enviado'),
              ('confirmado','Confirmado'),('pagado','Pagado'),('entregado','Entregado')]
    carrito          = models.ForeignKey(Carrito, on_delete=models.PROTECT)
    cliente          = models.ForeignKey(Cliente, on_delete=models.PROTECT)
    subtotal         = models.DecimalField(max_digits=10, decimal_places=2)
    descuento        = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    total            = models.DecimalField(max_digits=10, decimal_places=2)
    metodo_contacto  = models.CharField(max_length=20,
                        choices=[('whatsapp','WhatsApp'),('telegram','Telegram')])
    estado           = models.CharField(max_length=20, choices=ESTADO, default='pendiente')
    creado_en        = models.DateTimeField(auto_now_add=True)
```

#### `facturacion/models.py`
```python
class Factura(models.Model):
    ESTADO = [('pendiente','Pendiente'),('pagada','Pagada'),('cancelada','Cancelada')]
    METODO_PAGO = [('efectivo','Efectivo'),('qr','QR'),('transferencia','Transferencia')]
    numero_secuencial = models.IntegerField(unique=True)
    cita              = models.ForeignKey(Cita, null=True, blank=True,
                            on_delete=models.SET_NULL)
    pedido            = models.ForeignKey(Pedido, null=True, blank=True,
                            on_delete=models.SET_NULL)
    cliente           = models.ForeignKey(Cliente, on_delete=models.PROTECT)
    subtotal          = models.DecimalField(max_digits=10, decimal_places=2)
    impuesto          = models.DecimalField(max_digits=8, decimal_places=2)
    total             = models.DecimalField(max_digits=10, decimal_places=2)
    estado            = models.CharField(max_length=20, choices=ESTADO, default='pendiente')
    metodo_pago       = models.CharField(max_length=20, choices=METODO_PAGO)
    fecha_emision     = models.DateTimeField(auto_now_add=True)

class Pago(models.Model):
    factura              = models.ForeignKey(Factura, on_delete=models.CASCADE)
    monto                = models.DecimalField(max_digits=10, decimal_places=2)
    referencia_transaccion = models.CharField(max_length=200, blank=True)
    estado               = models.CharField(max_length=20,
                            choices=[('completado','Completado'),
                                     ('pendiente','Pendiente'),('fallido','Fallido')])
    fecha                = models.DateTimeField(auto_now_add=True)
```

#### `notificaciones/models.py`
```python
class Notificacion(models.Model):
    TIPO_CANAL = [('email','Email'),('whatsapp','WhatsApp'),('sms','SMS')]
    TIPO_EVENTO = [
        ('confirmacion','Confirmación'),
        ('recordatorio_24h','Recordatorio 24h'),
        ('recordatorio_2h','Recordatorio 2h'),
        ('listo_recoger','Listo para recoger'),
        ('encuesta','Encuesta post-servicio'),
        ('bajo_stock','Alerta bajo stock'),
    ]
    destinatario       = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    tipo_canal         = models.CharField(max_length=20, choices=TIPO_CANAL)
    tipo_evento        = models.CharField(max_length=30, choices=TIPO_EVENTO)
    destino            = models.CharField(max_length=200)  # email o teléfono
    mensaje            = models.TextField()
    fecha_programacion = models.DateTimeField()
    fecha_envio        = models.DateTimeField(null=True)
    exitoso            = models.BooleanField(default=False)
    intentos           = models.IntegerField(default=0)
    cita               = models.ForeignKey(Cita, null=True, blank=True,
                            on_delete=models.SET_NULL)
```

---

## 6. Mapa de URLs

```
/                           → página de inicio / login redirect
/auth/
  login/                    → iniciar sesión
  logout/                   → cerrar sesión
  registro/                 → auto-registro clientes
  activar/<token>/          → activar cuenta por email
  recuperar-password/       → solicitar reset
  reset/<token>/            → formulario nueva contraseña
  setup-2fa/                → configurar Google Authenticator
  verificar-2fa/            → ingresar código TOTP

/dashboard/                 → panel según rol

/mascotas/
  lista/                    → mis mascotas (cliente) / todas (admin/recepción)
  nueva/                    → registrar mascota
  <id>/                     → detalle mascota
  <id>/editar/              → editar ficha
  <id>/historial/           → historial completo

/agenda/
  /                         → calendario maestro
  cita/nueva/               → crear cita
  cita/<id>/                → detalle cita
  cita/<id>/reprogramar/    → reprogramar
  cita/<id>/cancelar/       → cancelar
  disponibilidad/           → configurar horarios por groomer
  bloqueos/                 → gestionar bloqueos

/grooming/
  ficha/<id>/               → ver/editar ficha de servicio
  ficha/<id>/checklist/     → marcar checklist
  ficha/<id>/fotos/         → subir fotos antes/después
  ficha/<id>/cerrar/        → cerrar ficha (valida checklist)

/inventario/
  productos/                → lista de productos
  productos/nuevo/          → agregar producto
  productos/<id>/editar/    → editar
  insumos/salida/           → registrar salida para servicio
  alertas/                  → alertas de bajo stock

/tienda/
  catalogo/                 → catálogo público
  producto/<id>/            → detalle producto
  carrito/                  → ver carrito
  carrito/agregar/          → agregar item (AJAX)
  carrito/pedido-whatsapp/  → generar link WhatsApp

/facturacion/
  facturas/                 → lista facturas
  facturas/<id>/            → ver factura
  facturas/<id>/recibo/     → generar recibo PDF
  pagos/registrar/          → registrar pago

/reportes/
  dashboard/                → KPIs principales
  ocupacion/                → % ocupación por groomer/franja
  ventas/                   → ticket estimado vs real
  inventario-critico/       → productos bajo stock
  top-servicios/            → ranking servicios
  exportar/                 → exportar PDF/CSV
```

---

## 7. Módulo de Seguridad

### 7.1 Sistema RBAC (decoradores Django)

```python
# apps/usuarios/decorators.py

def requiere_rol(*roles_permitidos):
    """
    Uso: @requiere_rol('admin', 'recepcion')
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('usuarios:login')
            if request.user.rol.nombre not in roles_permitidos:
                return render(request, '403.html', status=403)
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
```

### 7.2 Política de Contraseñas

| Regla | Valor |
|---|---|
| Longitud mínima | 8 caracteres |
| Complejidad | Mayúsculas + minúsculas + números + símbolos |
| Hashing | BCrypt con costo 12 |
| Token activación | Firmado, expira en 15 minutos |
| Bloqueo | 5 intentos fallidos → bloqueado 15 min |
| Sesión inactiva | Expiración a los 30 minutos |

### 7.3 Medidas implementadas

```
✓ CSRF tokens en todos los formularios (Django nativo)
✓ XSS: sanitización de inputs en forms.py
✓ SQL Injection: uso exclusivo del ORM Django (queries parametrizadas)
✓ 2FA TOTP para Administrador (pyotp)
✓ JWT para sesiones API (PyJWT)
✓ Borrado lógico: usuarios marcados como "inactivos", nunca eliminados
✓ Log de auditoría: quién, cuándo, IP, acción en cada operación crítica
✓ HTTPS en producción (TLS 1.3)
✓ AES-256 para datos sensibles en reposo
✓ Rate limiting: 100 peticiones/min por IP (middleware o django-ratelimit)
```

---

## 8. Reglas de Negocio Clave (implementación)

| Regla | Dónde se implementa |
|---|---|
| Duración ajustable por tamaño (+15–30%) | `agenda/validators.py → calcular_duracion()` |
| No solapamiento de citas | `UNIQUE(groomer_id, fecha_hora_inicio)` + validación en view |
| Doble booking solo si servicio lo permite | `Servicio.permite_doble_booking` — validación en view |
| Cerrar ficha requiere checklist completo | `grooming/views.py → cerrar_ficha()` valida antes |
| Descuento automático de inventario | `django signals → post_save` en `FichaGrooming` al cerrar |
| Precio congelado al agregar al carrito | `DetalleCarrito.precio_unitario` se copia al momento |
| Carritos expiran 7 días | `management command` o `cron` eliminando `expires_at < now` |
| Recordatorios 24h y 2h | `notificaciones/tasks.py` ejecutado por `cron` cada hora |
| Alerta bajo stock | `signals.py → post_save` en `Producto` cuando `stock ≤ stock_minimo` |
| Encuesta post-servicio | `signal → post_save` en `Cita` cuando estado cambia a "completada" |

---

## 9. Interfaces por Rol

### Administrador — `/dashboard/admin/`
- KPIs en tiempo real (citas del día, ingresos, ocupación)
- Gestión de usuarios y roles
- Configuración de precios y servicios
- Reportes completos con exportación PDF/CSV
- Alertas de inventario crítico

### Recepción — `/dashboard/recepcion/`
- Calendario maestro con drag & drop
- Bandeja de solicitudes de citas pendientes
- Punto de venta (cobros QR/efectivo/transferencia)
- Registro rápido de clientes y mascotas

### Groomer — `/dashboard/groomer/`
- Agenda personal del día/semana
- Apertura y cierre de fichas de servicio
- Checklist interactivo
- Subida de fotos antes/después
- Registro de insumos usados

### Cliente — `/dashboard/cliente/`
- Mis mascotas (perfil + historial + fotos)
- Solicitar / cancelar citas
- Historial de servicios
- Catálogo de tienda + carrito
- Descargar facturas electrónicas

---

## 10. Flujos Principales

```
FLUJO 1 — Agendar cita (Recepción)
  1. Recepción abre /agenda/cita/nueva/
  2. Selecciona mascota → servicio
  3. Sistema calcula duración (base ± ajuste por tamaño)
  4. Muestra slots disponibles del groomer
  5. Confirma → crea Cita(estado='agendada')
  6. Signal dispara Notificacion(tipo='confirmacion') al cliente

FLUJO 2 — Atender grooming (Groomer)
  1. Groomer ve su agenda → abre ficha de la cita
  2. Registra estado inicial de la mascota
  3. Marca checklist (mínimo 5 ítems)
  4. Sube fotos antes/después
  5. Al cerrar ficha → signal descuenta insumos del inventario
  6. Cita pasa a estado='completada'
  7. Notificacion 'listo_recoger' enviada al cliente

FLUJO 3 — Venta rápida (Tienda)
  1. Cliente navega catálogo → agrega al carrito
  2. Sistema congela precio en DetalleCarrito
  3. Cliente hace click "Pedir por WhatsApp"
  4. generar_mensaje_whatsapp() arma el texto con items + total + link
  5. Redirige a wa.me con el mensaje pre-armado

FLUJO 4 — Recordatorios automáticos (CRON)
  cron cada hora → tasks.py
    → busca Citas con fecha_hora_inicio entre 23h-25h → envía recordatorio_24h
    → busca Citas con fecha_hora_inicio entre 1h-3h   → envía recordatorio_2h
    → registra en Notificacion.fecha_envio y .exitoso
```

---

## 11. Integraciones

| Integración | Implementación |
|---|---|
| WhatsApp | URL dinámica `wa.me/?text=...` generada en `tienda/utils.py` |
| Telegram | URL `t.me/share/url?text=...` generada en `tienda/utils.py` |
| Email (activación/notificaciones) | `django.core.mail.send_mail()` via SMTP |
| QR de pago | Generación de imagen QR con librería `qrcode` |
| Fotos (subida) | `ImageField` de Django + carpeta `media/mascotas/fotos/` |

---

## 12. Requisitos No Funcionales

| Atributo | Especificación |
|---|---|
| Usabilidad | Flujo principal en máximo 3 clics (agendar, cobrar) |
| Multiplataforma | PWA-ready, diseño responsivo (escritorio/tablet/móvil) |
| Rendimiento | Carga de página < 2 segundos en local |
| Seguridad | JWT 1h, 2FA Admin, BCrypt, HTTPS, RBAC |
| Disponibilidad | Sistema restaurable en < 4 horas (RTO) |
| Recuperación de datos | Pérdida máxima de 15 minutos (RPO con backup SQLite) |
| Accesibilidad | Contraste mínimo WCAG AA, etiquetas ARIA en formularios |

---

## 13. Criterios de Aceptación (Checklist de entrega)

| # | Módulo | Criterio | Estado |
|---|---|---|---|
| 1 | Agenda | Un servicio de 60' no puede asignarse en un slot de 30' | ☐ |
| 2 | Capacidad | No se crean más citas que la capacidad del groomer | ☐ |
| 3 | Mascotas | Un cliente puede registrar varias mascotas | ☐ |
| 4 | Grooming | El checklist es obligatorio para cerrar la ficha | ☐ |
| 5 | Notificaciones | El cliente recibe recordatorios 24h/2h y "Listo para recoger" | ☐ |
| 6 | Inventario | El sistema descuenta stock al cerrar la ficha de grooming | ☐ |
| 7 | Seguridad | Acceso con autenticación y roles diferenciados (RBAC) | ☐ |
| 8 | Tienda | El pedido genera correctamente el mensaje WhatsApp/Telegram | ☐ |
| 9 | Autenticación | Token de activación expira en 15 minutos | ☐ |
| 10 | Reportes | Un cliente NO puede ver ventas del administrador | ☐ |

---

## 14. Plan de Implementación — 2 Semanas

### Semana 1
| Día | Tarea |
|---|---|
| 1–2 | Setup del proyecto Django, modelos: Usuario, Rol, Cliente, Mascota, Groomer, Servicio |
| 3 | Módulo de autenticación: registro, login, activación por email, RBAC |
| 4 | Agenda: disponibilidad, slots, creación de citas con validaciones |
| 5 | Grooming: ficha técnica, checklist, cierre con descuento de inventario |

### Semana 2
| Día | Tarea |
|---|---|
| 6–7 | Catálogo, carrito, pedido WhatsApp/Telegram |
| 8 | Notificaciones: confirmación, recordatorios, "listo para recoger" |
| 9 | Reportes: ocupación por día/groomer, ventas diarias |
| 10 | Fotos antes/después, 2FA para Admin, pruebas UAT finales |

---

## 15. Dependencias del Proyecto (`requirements.txt`)

```
django>=5.0
Pillow              # ImageField (fotos de mascotas)
PyJWT               # tokens JWT para sesiones
pyotp               # 2FA TOTP (Google Authenticator)
qrcode              # generación de QR para 2FA y pagos
bcrypt              # hashing de contraseñas (alternativa a PBKDF2)
django-ratelimit    # rate limiting en vistas
python-dotenv       # cargar variables desde .env
```

---

## 16. Variables de Entorno (`.env`)

```env
SECRET_KEY=tu_clave_secreta_django
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Email
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=tu_correo@gmail.com
EMAIL_HOST_PASSWORD=tu_app_password

# Media
MEDIA_URL=/media/
MEDIA_ROOT=media/
```

---

*Documento generado para el informe del Proyecto Pet Spa — Gestión de Sistema Web/Móvil para Spa & Tienda de Mascotas.*
