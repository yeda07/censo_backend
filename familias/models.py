from django.db import models

# Create your models here.
class Familia(models.Model):
    numero_familia = models.PositiveIntegerField(null=True)
    nombre_flia =models.CharField(max_length=150,null=True)
    