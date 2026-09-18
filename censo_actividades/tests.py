from django.test import TestCase

# Create your tests here.
from datetime import timedelta
from decimal import Decimal

from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from actividades.models import Actividad
from censo_actividades.models import CensoActividad
from censo_actividades.services import actualizar_actividades_vencidas
from censos.models import Censo
from multas.models import Multa
from users.models import User


class ActividadWorkflowTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='operador', email='operador@example.test', password='TestPassword123!'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.censo = Censo.objects.create(vigencia='2026')
        self.actividad = Actividad.objects.create(
            descripcion='Trabajo comunitario',
            fecha_limite=timezone.localdate() + timedelta(days=1),
        )

    def asignar(self):
        response = self.client.post(
            '/censo_actividad/',
            {'censo': self.censo.id, 'actividad': self.actividad.id},
            format='json',
        )
        self.assertEqual(response.status_code, 201, response.data)
        return CensoActividad.objects.get(pk=response.data['id'])

    def test_pending_blocks_certificate_without_fine(self):
        asignacion = self.asignar()
        self.assertEqual(asignacion.estado, CensoActividad.PENDIENTE)
        self.assertFalse(Multa.objects.filter(censo_actividad=asignacion).exists())

        response = self.client.get(f'/censo/{self.censo.id}/paz-y-salvo/')
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.data['habilitado'])

    def test_deadline_day_is_still_pending(self):
        self.actividad.fecha_limite = timezone.localdate()
        self.actividad.save(update_fields=['fecha_limite'])
        asignacion = self.asignar()

        actualizar_actividades_vencidas()
        asignacion.refresh_from_db()
        self.assertEqual(asignacion.estado, CensoActividad.PENDIENTE)
        self.assertFalse(asignacion.multas.exists())

    def test_expiration_creates_one_fine_and_late_completion_removes_it(self):
        asignacion = self.asignar()
        self.actividad.fecha_limite = timezone.localdate() - timedelta(days=1)
        self.actividad.save(update_fields=['fecha_limite'])

        actualizar_actividades_vencidas()
        actualizar_actividades_vencidas()
        asignacion.refresh_from_db()
        self.assertEqual(asignacion.estado, CensoActividad.NO_REALIZADA)
        self.assertEqual(Multa.objects.filter(censo_actividad=asignacion).count(), 1)
        self.assertEqual(asignacion.multas.get().monto, Decimal('100.00'))
        self.assertFalse(self.client.get(f'/censo/{self.censo.id}/paz-y-salvo/').data['habilitado'])

        response = self.client.patch(
            f'/censo_actividad/{asignacion.id}/', {'estado': CensoActividad.TERMINADA}, format='json'
        )
        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(response.data['fecha_realizacion'], str(timezone.localdate()))
        self.assertFalse(Multa.objects.filter(censo_actividad=asignacion).exists())
        self.assertTrue(self.client.get(f'/censo/{self.censo.id}/paz-y-salvo/').data['habilitado'])

    def test_completed_before_deadline_never_gets_fine(self):
        asignacion = self.asignar()
        response = self.client.patch(
            f'/censo_actividad/{asignacion.id}/', {'estado': CensoActividad.TERMINADA}, format='json'
        )
        self.assertEqual(response.status_code, 200, response.data)
        self.actividad.fecha_limite = timezone.localdate() - timedelta(days=1)
        self.actividad.save(update_fields=['fecha_limite'])

        actualizar_actividades_vencidas()
        asignacion.refresh_from_db()
        self.assertEqual(asignacion.estado, CensoActividad.TERMINADA)
        self.assertFalse(Multa.objects.filter(censo_actividad=asignacion).exists())

    def test_assignment_past_deadline_is_overdue_immediately(self):
        self.actividad.fecha_limite = timezone.localdate() - timedelta(days=1)
        self.actividad.save(update_fields=['fecha_limite'])
        asignacion = self.asignar()
        self.assertEqual(asignacion.estado, CensoActividad.NO_REALIZADA)
        self.assertEqual(asignacion.multas.count(), 1)

    def test_fines_cannot_be_created_manually(self):
        asignacion = self.asignar()
        response = self.client.post(
            '/multa/', {'censo_actividad': asignacion.id, 'monto': '100.00'}, format='json'
        )
        self.assertEqual(response.status_code, 405)

    def test_create_activity_then_assign_to_census(self):
        created = self.client.post('/actividad/', {
            'descripcion': 'Jornada de siembra',
            'fecha_limite': str(timezone.localdate() + timedelta(days=7)),
        }, format='json')
        self.assertEqual(created.status_code, 201, created.data)

        assigned = self.client.post('/censo_actividad/', {
            'censo': self.censo.id,
            'actividad': created.data['id'],
        }, format='json')
        self.assertEqual(assigned.status_code, 201, assigned.data)
        self.assertEqual(assigned.data['estado'], CensoActividad.PENDIENTE)
        self.assertEqual(assigned.data['actividad'], created.data['id'])
