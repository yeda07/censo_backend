from django.db import models

# Create your models here.
class Persona(models.Model):
    SECUNDARIA = 'SC'
    PRIMARIA = 'PR'
    UNIVERSITARIA = 'UN'
    NINGUNO = 'NI'
    # Opciones de elección
    CHOICES_ESCOLARIDAD = [
        (SECUNDARIA, 'Secundaria'),
        (PRIMARIA, 'Primaria'),
        (UNIVERSITARIA, 'Universitaria'),
        (NINGUNO, 'Ninguno'),
    ]
    
    PADRE = 'PA'
    MADRE = 'MA'
    CONYUGUE = 'CO'
    HERMANO = 'HE'
    CABEZA_DE_FAMILIA = 'CF'
    ESPOSA = 'ES'
    HIJO = 'HI'
    YERNO = 'YR'
    NUERA = 'NU'
    SUEGRO = 'SU'
    SOBRINO = 'SO'
    CUNADO = 'CU'
    TIO = 'TI'
    ABUELO = 'AB'

    # Lista de opciones de parentesco
    CHOICES_PARENTESCO = [
        (PADRE, 'Padre'),
        (MADRE, 'Madre'),
        (CONYUGUE, 'Conyugue'),
        (HERMANO, 'Hermano(a)'),
        (CABEZA_DE_FAMILIA, 'Cabeza De Familia'),
        (ESPOSA, 'Esposa'),
        (HIJO, 'Hijo (a)'),
        (YERNO, 'Yerno'),
        (NUERA, 'Nuera'),
        (SUEGRO, 'Suegro (a)'),
        (SOBRINO, 'Sobrino (a)'),
        (CUNADO, 'Cuñado (a)'),
        (TIO, 'Tio (a)'),
        (ABUELO, 'Abuelo (a)'),
    ]
    
    CC = 'CC'
    RC = 'RC'
    NUIP = 'NUIP'
    TI = 'TI'

    # Lista de opciones de tipo de documento
    CHOICES_TIPO_DOCUMENTO = [
        (CC, 'Cedula'),
        (RC, 'Registro Civil'),
        (NUIP, 'Numero único de Identificación Personal'),
        (TI, 'Tarjeta de Identidad'),
    ]
    
    familida_id = models.ForeignKey('familias.Familia',on_delete=models.SET_NULL,null=True,blank=True)
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=150)
    tipo_documento = models.CharField(max_length=4, choices=CHOICES_TIPO_DOCUMENTO, null=True)
    numero_documento =models.IntegerField()
    exp_documento=models.DateField()
    fecha_nacimiento=models.DateField()
    parentesco = models.CharField(max_length=2, choices=CHOICES_PARENTESCO, null=True)
    sexo =models.CharField(max_length=100)
    estado_civil =models.CharField(max_length=100)
    profesion =models.CharField(max_length=150)
    escolaridad = models.CharField(max_length=2, choices=CHOICES_ESCOLARIDAD, null=True)
    integrantes = models.IntegerField()
    direccion = models.CharField(max_length=150)
    telefono = models.CharField(max_length=150)
    
    usuario = models.CharField(max_length=150)
