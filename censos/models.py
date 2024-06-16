from django.db import models

# Create your models here.
class Censo(models.Model):
    vigencia = models.CharField(max_length=150,null=False)
    resguardo_ind = models.PositiveIntegerField(null=True)
    comunidad_ind = models.PositiveIntegerField(null=True)
    persona = models.ForeignKey('personas.Persona',on_delete=models.SET_NULL,null=True)
    documento_pdf = models.FileField(upload_to='pdfs/', null=True, blank=True)