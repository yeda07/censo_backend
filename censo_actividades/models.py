from django.db import models

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
    
    censo = models.ForeignKey('censos.Censo', on_delete=models.CASCADE)
    actividad = models.ForeignKey('actividades.Actividad', on_delete=models.CASCADE)
    estado = models.CharField(max_length=1, choices=CHOICES_ESTADO, default=PENDIENTE)