from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from censo_actividades.models import CensoActividad
from multas.models import Multa


def actualizar_actividades_vencidas(censo_id=None, hoy=None):
    hoy = hoy or timezone.localdate()
    pendientes = CensoActividad.objects.filter(
        estado__in=[CensoActividad.PENDIENTE, CensoActividad.EN_TRANS_CURSO],
        actividad__fecha_limite__lt=hoy,
    )
    if censo_id is not None:
        pendientes = pendientes.filter(censo_id=censo_id)

    with transaction.atomic():
        for asignacion in pendientes.select_for_update():
            asignacion.estado = CensoActividad.NO_REALIZADA
            asignacion.save(update_fields=['estado'])
            Multa.objects.get_or_create(
                censo_actividad=asignacion,
                defaults={'monto': Decimal('100.00')},
            )


@transaction.atomic
def confirmar_actividad_realizada(asignacion):
    asignacion.estado = CensoActividad.TERMINADA
    asignacion.fecha_realizacion = timezone.localdate()
    asignacion.save(update_fields=['estado', 'fecha_realizacion'])
    asignacion.multas.all().delete()
    return asignacion
