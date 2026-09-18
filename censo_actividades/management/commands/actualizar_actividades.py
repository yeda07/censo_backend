from django.core.management.base import BaseCommand

from censo_actividades.services import actualizar_actividades_vencidas


class Command(BaseCommand):
    help = 'Marca actividades vencidas como no realizadas y genera sus multas.'

    def handle(self, *args, **options):
        actualizar_actividades_vencidas()
        self.stdout.write(self.style.SUCCESS('Actividades vencidas actualizadas.'))
