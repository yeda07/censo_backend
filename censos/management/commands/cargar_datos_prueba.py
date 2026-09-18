from datetime import date, timedelta

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from actividades.models import Actividad
from censo_actividades.models import CensoActividad
from censo_actividades.services import actualizar_actividades_vencidas, confirmar_actividad_realizada
from censos.models import Censo
from familias.models import Familia
from personas.models import Persona


class Command(BaseCommand):
    help = 'Carga familias, censos y actividades ficticias para desarrollo local.'

    @transaction.atomic
    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError('Los datos de prueba solo se cargan en desarrollo.')
        hoy = timezone.localdate()
        familia_a, _ = Familia.objects.get_or_create(
            numero_familia=90001,
            nombre_flia='DEMO - Familia A',
        )
        familia_b, _ = Familia.objects.get_or_create(
            numero_familia=90002,
            nombre_flia='DEMO - Familia B',
        )

        personas = []
        for nombre, documento, familia, parentesco in (
            ('Ana DEMO', 900001001, familia_a, Persona.CABEZA_DE_FAMILIA),
            ('Bruno DEMO', 900001002, familia_a, Persona.HIJO),
            ('Carla DEMO', 900001003, familia_b, Persona.CABEZA_DE_FAMILIA),
        ):
            persona, _ = Persona.objects.get_or_create(
                numero_documento=documento,
                defaults={
                    'familida_id': familia,
                    'nombres': nombre,
                    'apellidos': 'Ejemplo',
                    'tipo_documento': Persona.CC,
                    'exp_documento': date(2015, 1, 15),
                    'fecha_nacimiento': date(1990, 5, 20),
                    'parentesco': parentesco,
                    'sexo': 'No especificado',
                    'estado_civil': 'No especificado',
                    'profesion': 'Dato de prueba',
                    'escolaridad': Persona.SECUNDARIA,
                    'integrantes': 2 if familia == familia_a else 1,
                    'direccion': 'DIRECCION DE PRUEBA',
                    'telefono': '0000000000',
                    'usuario': 'DEMO',
                },
            )
            if persona.usuario != 'DEMO':
                raise CommandError(f'El documento {documento} ya pertenece a un registro real.')
            personas.append(persona)

        censos = [
            Censo.objects.get_or_create(
                persona=persona,
                vigencia=f'DEMO-{hoy.year}',
                defaults={'resguardo_ind': 1, 'comunidad_ind': 1},
            )[0]
            for persona in personas
        ]

        terminada, _ = Actividad.objects.get_or_create(
            descripcion='DEMO - Taller realizado',
            defaults={'fecha_limite': hoy - timedelta(days=1)},
        )
        pendiente, _ = Actividad.objects.get_or_create(
            descripcion='DEMO - Reunion proxima',
            defaults={'fecha_limite': hoy + timedelta(days=7)},
        )
        vencida, _ = Actividad.objects.get_or_create(
            descripcion='DEMO - Jornada vencida',
            defaults={'fecha_limite': hoy - timedelta(days=1)},
        )

        asignacion_terminada, _ = CensoActividad.objects.get_or_create(
            censo=censos[0], actividad=terminada,
        )
        if asignacion_terminada.estado != CensoActividad.TERMINADA:
            confirmar_actividad_realizada(asignacion_terminada)
        CensoActividad.objects.get_or_create(censo=censos[1], actividad=pendiente)
        CensoActividad.objects.get_or_create(censo=censos[2], actividad=vencida)
        actualizar_actividades_vencidas(censo_id=censos[2].id, hoy=hoy)

        self.stdout.write(self.style.SUCCESS(
            'Datos DEMO listos: Ana al dia, Bruno pendiente, Carla vencida con multa.'
        ))
