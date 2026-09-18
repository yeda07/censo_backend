from django.db import models
from django.core.validators import MinValueValidator

# Create your models here.
class Familia(models.Model):
    numero_familia = models.PositiveIntegerField(null=True)
    nombre_flia =models.CharField(max_length=150,null=True)


class MetaCensoFamiliar(models.Model):
    familia = models.ForeignKey(Familia, on_delete=models.CASCADE, related_name='metas_censo')
    vigencia = models.CharField(max_length=150)
    integrantes_previstos = models.PositiveIntegerField(validators=[MinValueValidator(1)])

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['familia', 'vigencia'], name='meta_familia_vigencia_unica'),
        ]
