from django.db import models

# Create your models here.
    
    
class Actividad(models.Model):
    descripcion = models.CharField(max_length=150,null=False)
    fecha_limite = models.DateField()
