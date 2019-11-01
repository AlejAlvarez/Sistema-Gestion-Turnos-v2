from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator

from app_informacion.models import ObraSocial, Especialidad

class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        (1, 'paciente'),
        (2, 'recepcionista'),
        (3, 'medico'),
        (4, 'administrador'),
    )

    user_type = models.PositiveSmallIntegerField(choices=USER_TYPE_CHOICES, null=True)
    # Validator del documento, ni idea si funciona: validators=[RegexValidator(regex='[0-9]{8}$', message='El documento introducido debe ser de 8 dígitos', code='nomatch')], 
    documento = models.BigIntegerField(unique=True, null=True)
    domicilio = models.CharField(max_length=100, null=True)
    # Validator del telefono, ídem que con el documento: validators=[RegexValidator(regex='+[0-9]{2,4}-[0-9]{6}$', message='Introduzca un numero de teléfono válido, con la forma "+011-123456", o sea: "+", característica provincial, "-" (guión), y por último número de teléfono. En caso de ser celular, omita el "15".')],
    telefono = models.BigIntegerField(null=True)
    nacimiento = models.DateTimeField(null=True)

class Paciente(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, primary_key=True)
    GENERO_CHOICES = (
        (1, "masculino"),
        (2, "femenino"),
    )

    genero = models.PositiveSmallIntegerField(choices=GENERO_CHOICES)
    penalizado = models.BooleanField(default=False)
    fecha_despenalizacion = models.DateTimeField(verbose_name="fecha de despenalización", blank=True, null=True)
    obra_social = models.ForeignKey(ObraSocial, on_delete=models.CASCADE)

class Medico(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, primary_key=True)
    # Validator del CUIL, ídem que con el documento: validators=[RegexValidator(regex='[0-9]{2}-[0-9]{8}-[0-9]$', message='La constancia de CUIL introducida debe ser de formato "XX-XXXXXXXX-X".', code='nomatch')], 
    cuil = models.BigIntegerField(unique=True)
    especialidad = models.ForeignKey(Especialidad, on_delete=models.CASCADE)
    
