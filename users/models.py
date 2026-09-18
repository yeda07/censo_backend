from django.db import models
from django.contrib.auth.models import AbstractUser




class User(AbstractUser):
    email=models.EmailField(unique=True)    
    USERNAME_FIELD="email"
    REQUIRED_FIELDS=['username']
    totp_secret = models.TextField(blank=True, default='')
    totp_last_counter = models.BigIntegerField(default=-1)
    recovery_code_hashes = models.JSONField(default=list, blank=True)
    auth_version = models.PositiveIntegerField(default=0)
    otp_failed_attempts = models.PositiveIntegerField(default=0)
    otp_locked_until = models.DateTimeField(null=True, blank=True)

    @property
    def two_factor_enabled(self):
        return bool(self.totp_secret)
    

""" 
Para crear un Usuario por primera vez debe de estar asi:

-- -----------------------------------------------------

class User(AbstractUser):
    pass

-- -----------------------------------------------------

Despues migrar:

py manage.py makemigrations
py manage.py migrate

-- -----------------------------------------------------

Ahora crear un super usuario:

py manage.py createsuperuser
maycolguerrero2021@itp.edu.co

-- -----------------------------------------------------

Despues lo dejamos como estaba: 

class User(AbstractUser):
    email=models.EmailField(unique=True)    
    USERNAME_FIELD="email"
    REQUIRED_FIELDS=[]

-- -----------------------------------------------------

Despues migrar:

py manage.py makemigrations
py manage.py migrate

-- -----------------------------------------------------

Y ahora ya podremos iniciar sesion con el Email

"""
