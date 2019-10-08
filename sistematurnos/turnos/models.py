from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.utils import timezone
from django.conf import settings

class User(AbstractUser):
    USER_TYPE_CHOICES = (
        (1, 'paciente'),
        (2, 'recepcionista'),
        (3, 'medico'),
        (4, 'administrador'),
    )

    user_type = models.PositiveSmallIntegerField(choices=USER_TYPE_CHOICES)

class Perfil(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=50)
    apellido = models.CharField(max_length=50)
    documento = models.BigIntegerField(validators=[RegexValidator(regex='[0-9]{8}$', message='El documento introducido debe ser de 8 dígitos', code='nomatch')], unique=True)
    domicilio = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    telefono = models.BigIntegerField(validators=[RegexValidator(regex='[0-9]{2,4}-[0-9]{6}$', message='Introduzca un numero de teléfono válido, con la forma "+011-123456", o sea: "+", característica provincial, "-" (guión), y por último número de teléfono. En caso de ser celular, omita el "15".')])
    nacimiento = models.DateTimeField()
    registro = models.DateTimeField(auto_now_add=True)
    ultima_conexion = models.DateTimeField()

    class Meta:
        abstract = True 

class ObraSocial(models.Model):
    nombre = models.CharField(max_length=100)

class Paciente(Perfil):
    GENERO_CHOICES = (
        (1, "masculino"),
        (2, "femenino"),
    )

    genero = models.PositiveSmallIntegerField(choices=GENERO_CHOICES)
    penalizado = models.BooleanField(default=False)
    fecha_penalizacion = models.DateTimeField()
    obra_social = models.ForeignKey(ObraSocial, on_delete=models.CASCADE)

class Recepcionista(Perfil):
    pass

class Administrador(Perfil):
    pass

class Especialidad(models.Model):
    nombre = models.CharField(max_length=100)

class Medico(Perfil):
    cuil = models.BigIntegerField(validators=[RegexValidator(regex='[0-9]{2}-[0-9]{8}-[0-9]$', message='La constancia de CUIL introducida debe ser de formato "XX-XXXXXXXX-X".', code='nomatch')], unique=True)
    especialidad = models.ForeignKey(Especialidad, on_delete=models.CASCADE)

class Solicitud(models.Model):
    pendiente = models.BooleanField(default=True)
    contenido = models.TextField()

class Turno(models.Model):
    ESTADO_CHOICES = (
        (1, "pendiente"),
        (2, "aceptado"),
        (3, "cancelado"),
        (4, "sobreturno"),
    )

    fecha = models.DateTimeField()
    estado = models.PositiveSmallIntegerField(choices=ESTADO_CHOICES)
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='paciente_a_atender')
    medico = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='medico_que_atiende')

class Sobreturno(Turno):
    prioridad = models.PositiveSmallIntegerField()

class TurnoCancelado(Turno):
    fecha_cancelado = models.DateTimeField(auto_now_add=True)
