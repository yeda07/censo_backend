from datetime import date, timedelta
from io import StringIO

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.db import connection, transaction
from django.utils import timezone

from actividades.models import Actividad
from censo_actividades.models import CensoActividad
from censo_actividades.services import actualizar_actividades_vencidas, confirmar_actividad_realizada
from censos.models import Censo
from familias.models import Familia, MetaCensoFamiliar
from personas.models import Persona


NOMBRES = ('Lina', 'Jorge', 'María', 'Carlos', 'Diana', 'Luis', 'Rosa', 'Mateo', 'Elena', 'Andrés', 'Sara', 'Iván')
EDADES = (68, 43, 17, 8, 32, 24, 5, 75, 19, 54, 12, 28)


class Command(BaseCommand):
    help = 'Carga un conjunto DEMO amplio para probar filtros, paginacion, reportes y paz y salvo.'

    @transaction.atomic
    def handle(self, *args, **options):
        if not settings.DEBUG or connection.vendor != 'sqlite':
            raise CommandError('Los datos de prueba ampliados solo se cargan en SQLite local de desarrollo.')

        call_command('cargar_datos_prueba', stdout=StringIO())
        hoy = timezone.localdate()
        vigencia = f'DEMO-{hoy.year}'
        anterior = f'DEMO-{hoy.year - 1}'
        censos_actuales = []

        for indice in range(1, 33):
            numero = 91000 + indice
            nombre_familia = f'DEMO - Familia {indice:02d}'
            familia, _ = Familia.objects.get_or_create(
                numero_familia=numero, defaults={'nombre_flia': nombre_familia},
            )
            if familia.nombre_flia != nombre_familia:
                raise CommandError(f'El numero de familia {numero} ya esta en uso.')

            integrantes = 0 if indice == 32 else 12 if indice == 1 else 3
            previstos = 2 if indice == 32 else 5 if indice == 2 else integrantes + (1 if indice % 4 == 0 else 0)
            MetaCensoFamiliar.objects.get_or_create(
                familia=familia, vigencia=vigencia,
                defaults={'integrantes_previstos': previstos},
            )

            for miembro in range(1, integrantes + 1):
                documento = 910000000 + indice * 100 + miembro
                edad = EDADES[(indice + miembro - 2) % len(EDADES)]
                nacimiento = date(hoy.year - edad, 1, 1)
                expedicion = date(min(hoy.year, nacimiento.year + 10), 1, 1)
                persona, _ = Persona.objects.get_or_create(
                    numero_documento=documento,
                    defaults={
                        'familida_id': familia,
                        'nombres': NOMBRES[(indice + miembro - 2) % len(NOMBRES)],
                        'apellidos': f'Prueba {indice:02d}',
                        'tipo_documento': Persona.TI if edad < 18 else Persona.CC,
                        'exp_documento': expedicion,
                        'fecha_nacimiento': nacimiento,
                        'parentesco': Persona.CABEZA_DE_FAMILIA if miembro == 1 else Persona.HIJO,
                        'sexo': 'F' if miembro % 2 else 'M',
                        'estado_civil': 'Soltero(a)',
                        'profesion': 'Dato de prueba',
                        'escolaridad': Persona.PRIMARIA if edad < 18 else Persona.SECUNDARIA,
                        'discapacidad': 'SI' if (indice + miembro) % 9 == 0 else 'NO',
                        'integrantes': integrantes,
                        'direccion': f'DIRECCION DEMO {numero}',
                        'telefono': '0000000000',
                        'usuario': 'DEMO',
                    },
                )
                if persona.usuario != 'DEMO' or persona.familida_id_id != familia.id:
                    raise CommandError(f'El documento {documento} ya pertenece a otro registro.')
                if not persona.discapacidad:
                    persona.discapacidad = 'SI' if (indice + miembro) % 9 == 0 else 'NO'
                    persona.save(update_fields=['discapacidad'])

                censo, _ = Censo.objects.get_or_create(
                    persona=persona, vigencia=vigencia,
                    defaults={'resguardo_ind': 1, 'comunidad_ind': indice % 4 + 1},
                )
                censos_actuales.append(censo)
                if miembro % 6 == 0 or (indice + miembro) % 5 == 0:
                    Censo.objects.get_or_create(
                        persona=persona, vigencia=anterior,
                        defaults={'resguardo_ind': 1, 'comunidad_ind': indice % 4 + 1},
                    )

        actividades = []
        for indice in range(1, 61):
            fecha_limite = hoy + timedelta(days=15) if indice % 3 == 0 else hoy - timedelta(days=3)
            actividad, _ = Actividad.objects.get_or_create(
                descripcion=f'DEMO - Actividad {indice:02d}',
                defaults={'fecha_limite': fecha_limite},
            )
            actividades.append(actividad)

        censos_vencidos = set()
        for indice in range(90):
            censo = censos_actuales[indice % len(censos_actuales)]
            actividad = actividades[indice % len(actividades)]
            asignacion, creada = CensoActividad.objects.get_or_create(censo=censo, actividad=actividad)
            if not creada:
                continue
            if (indice + 1) % 3 == 2:
                confirmar_actividad_realizada(asignacion)
            elif (indice + 1) % 3 == 1:
                censos_vencidos.add(censo.id)

        for censo_id in censos_vencidos:
            actualizar_actividades_vencidas(censo_id=censo_id, hoy=hoy)

        self.stdout.write(self.style.SUCCESS(
            f'Datos DEMO ampliados listos para {vigencia}: 32 familias, 60 actividades y 90 asignaciones previstas.'
        ))
