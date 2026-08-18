"""
Pobla la base de datos con datos iniciales.
Uso: python manage.py seed
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password


class Command(BaseCommand):
    help = 'Crea roles, usuarios y datos iniciales'

    def handle(self, *args, **options):
        from apps.usuarios.models import Rol, Usuario
        from apps.agenda.models import Groomer, Servicio, DisponibilidadGroomer
        from apps.mascotas.models import Cliente
        from apps.inventario.models import Categoria, Producto
        from apps.grooming.models import ItemChecklistTemplate

        self.stdout.write('Creando roles...')
        roles = {}
        for nombre, desc in [
            ('admin',     'Acceso total al sistema'),
            ('recepcion', 'Gestión de citas y pagos'),
            ('groomer',   'Atención de mascotas'),
            ('cliente',   'Dueño de mascota'),
        ]:
            r, _ = Rol.objects.get_or_create(nombre=nombre, defaults={'descripcion': desc})
            roles[nombre] = r

        self.stdout.write('Creando usuarios...')
        usuarios = [
            {'email': 'admin@petspa.com',      'first': 'Admin',   'last': 'Principal', 'rol': 'admin',     'username': 'admin'},
            {'email': 'recepcion@petspa.com',  'first': 'María',   'last': 'Recepción', 'rol': 'recepcion', 'username': 'recepcion'},
            {'email': 'groomer1@petspa.com',   'first': 'Carlos',  'last': 'Groomer',   'rol': 'groomer',   'username': 'groomer1'},
            {'email': 'cliente@petspa.com',    'first': 'Juan',    'last': 'Pérez',     'rol': 'cliente',   'username': 'cliente1'},
        ]
        for ud in usuarios:
            if not Usuario.objects.filter(email=ud['email']).exists():
                u = Usuario.objects.create(
                    username=ud['username'],
                    email=ud['email'],
                    first_name=ud['first'],
                    last_name=ud['last'],
                    rol=roles[ud['rol']],
                    email_verificado=True,
                    is_active=True,
                    is_staff=ud['rol'] == 'admin',
                    is_superuser=ud['rol'] == 'admin',
                    password=make_password('Admin123!'),
                )
                self.stdout.write(f'  Creado: {u.email}')

        self.stdout.write('Creando groomers...')
        groomer_user = Usuario.objects.get(email='groomer1@petspa.com')
        g, _ = Groomer.objects.get_or_create(
            usuario=groomer_user,
            defaults={'especialidad': 'Corte fino y baño', 'capacidad_simultanea': 2}
        )
        for dia in [1, 2, 3, 4, 5]:  # Lun-Vie
            DisponibilidadGroomer.objects.get_or_create(
                groomer=g,
                dia_semana=dia,
                defaults={'hora_inicio': '09:00', 'hora_fin': '18:00',
                          'intervalo_descanso': {'inicio': '12:30', 'fin': '14:00'}}
            )

        self.stdout.write('Creando servicios...')
        servicios = [
            {'nombre': 'Baño Rápido',           'duracion': 30,  'precio': 35},
            {'nombre': 'Baño Completo',          'duracion': 60,  'precio': 55},
            {'nombre': 'Corte y Peinado',        'duracion': 90,  'precio': 80},
            {'nombre': 'Servicio Completo',      'duracion': 120, 'precio': 120},
            {'nombre': 'Corte de Uñas',          'duracion': 15,  'precio': 20},
        ]
        for sd in servicios:
            Servicio.objects.get_or_create(
                nombre=sd['nombre'],
                defaults={'duracion_base_minutos': sd['duracion'], 'precio_base': sd['precio']}
            )

        self.stdout.write('Creando checklist items...')
        items = ['Baño', 'Secado', 'Corte', 'Cepillado', 'Uñas', 'Oídos', 'Glándulas', 'Perfume']
        for nombre in items:
            ItemChecklistTemplate.objects.get_or_create(nombre=nombre)

        self.stdout.write('Creando categorías e inventario...')
        cat_higiene, _ = Categoria.objects.get_or_create(nombre='Higiene')
        cat_alimento, _ = Categoria.objects.get_or_create(nombre='Alimentos')
        cat_juguetes, _ = Categoria.objects.get_or_create(nombre='Juguetes')
        cat_insumos,  _ = Categoria.objects.get_or_create(nombre='Insumos Grooming')

        productos = [
            {'nombre': 'Shampoo Lavanda', 'sku': 'SH-001', 'precio': 25, 'stock': 20, 'cat': cat_higiene, 'insumo': False},
            {'nombre': 'Shampoo Neutro',  'sku': 'SH-002', 'precio': 22, 'stock': 15, 'cat': cat_higiene, 'insumo': False},
            {'nombre': 'Alimento Premium 3kg', 'sku': 'AL-001', 'precio': 85, 'stock': 30, 'cat': cat_alimento, 'insumo': False},
            {'nombre': 'Alimento Premium 1kg', 'sku': 'AL-002', 'precio': 35, 'stock': 50, 'cat': cat_alimento, 'insumo': False},
            {'nombre': 'Juguete Pelota', 'sku': 'JG-001', 'precio': 15, 'stock': 25, 'cat': cat_juguetes, 'insumo': False},
            {'nombre': 'Shampoo Profesional (insumo)', 'sku': 'INS-001', 'precio': 45, 'stock': 8, 'cat': cat_insumos, 'insumo': True},
            {'nombre': 'Perfume Canino (insumo)', 'sku': 'INS-002', 'precio': 30, 'stock': 3, 'cat': cat_insumos, 'insumo': True},
        ]
        for pd in productos:
            Producto.objects.get_or_create(
                sku=pd['sku'],
                defaults={
                    'nombre': pd['nombre'],
                    'categoria': pd['cat'],
                    'precio_base': pd['precio'],
                    'stock_actual': pd['stock'],
                    'stock_minimo': 5,
                    'es_insumo': pd['insumo'],
                }
            )

        self.stdout.write('Creando perfil de cliente...')
        cliente_user = Usuario.objects.get(email='cliente@petspa.com')
        Cliente.objects.get_or_create(
            usuario=cliente_user,
            defaults={'nombre': 'Juan Pérez', 'ci': '12345678', 'telefono': '70000001'}
        )

        self.stdout.write(self.style.SUCCESS(
            '\nDatos iniciales cargados correctamente.\n\n'
            'Usuarios creados (contrasena: Admin123!):\n'
            '  admin@petspa.com      -> Administrador\n'
            '  recepcion@petspa.com  -> Recepcion\n'
            '  groomer1@petspa.com   -> Groomer\n'
            '  cliente@petspa.com    -> Cliente\n'
        ))
