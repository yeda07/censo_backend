from django.db import models

# Create your models here.

class Multa(models.Model):
    censo_actividad = models.ForeignKey('censo_actividades.CensoActividad', on_delete=models.CASCADE, related_name='multas')
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    pagada = models.BooleanField(default=False)
    fecha_pago = models.DateField(null=True, blank=True)  # Nuevo campo para capturar la fecha de pago
    
    def __str__(self):
        return f"{self.censo_actividad} - {'Pendiente' if self.pagada else 'Pagada'}"
