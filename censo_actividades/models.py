from django.db import models

class CensoActividad(models.Model):
    TERMINADA = 'T'
    EN_TRANS_CURSO = 'E'
    PENDIENTE = 'P'
    NO_REALIZADA = 'N'
    
    CHOICES_ESTADO = [
        (TERMINADA, 'Terminada'),
        (EN_TRANS_CURSO, 'En Transcurso'),
        (PENDIENTE, 'Pendiente'),
        (NO_REALIZADA, 'No realizada'),
    ]
    
    censo = models.ForeignKey('censos.Censo', on_delete=models.SET_NULL, null=True, blank=True)
    actividad = models.ForeignKey('actividades.Actividad', on_delete=models.SET_NULL, null=True, blank=True)
    estado = models.CharField(max_length=1, choices=CHOICES_ESTADO, default=PENDIENTE)
    fecha_realizacion = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.censo} - {self.actividad} ({self.get_estado_display()})"
