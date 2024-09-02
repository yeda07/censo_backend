from django.db import models
from django.contrib.auth.models import AbstractUser




class User(AbstractUser):
    email=models.EmailField(unique=True)    
    USERNAME_FIELD="email"
    REQUIRED_FIELDS=[]
    

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
