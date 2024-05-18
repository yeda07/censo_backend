from django.db import models

from multas.models import Multa

# Create your models here.
class CensoActividad(models.Model):
    TERMINADA = 'T'
    EN_TRANS_CURSO = 'E'
    PENDIENTE = 'P'
    
    CHOICES_ESTADO = [
        (TERMINADA, 'Terminada'),
        (EN_TRANS_CURSO, 'En Transcurso'),
        (PENDIENTE, 'Pendiente'),
    ]
    
    censo = models.ForeignKey('censos.Censo', on_delete=models.SET_NULL, null=True, blank=True)
    actividad = models.ForeignKey('actividades.Actividad', on_delete=models.SET_NULL, null=True, blank=True)
    estado = models.CharField(max_length=1, choices=CHOICES_ESTADO, default=PENDIENTE)

    def save(self, *args, **kwargs):
        # Si el estado cambia a "Pendiente", crea una multa
        if self.pk and self.estado == self.PENDIENTE:
            Multa.objects.get_or_create(censo_actividad=self, defaults={'monto': 100.00})  # Asigna el monto que desees
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.censo} - {self.actividad} ({self.get_estado_display()})"

    