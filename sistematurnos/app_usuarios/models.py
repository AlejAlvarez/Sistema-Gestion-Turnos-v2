from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from datetime import datetime, timedelta

from app_informacion.models import ObraSocial, Especialidad

class CustomUser(AbstractUser):
    # Validator del documento, ni idea si funciona: validators=[RegexValidator(regex='[0-9]{8}$', message='El documento introducido debe ser de 8 dígitos', code='nomatch')], 
    documento = models.BigIntegerField(unique=True, null=True)
    domicilio = models.CharField(max_length=100, null=True)
    # Validator del telefono, ídem que con el documento: validators=[RegexValidator(regex='+[0-9]{2,4}-[0-9]{6}$', message='Introduzca un numero de teléfono válido, con la forma "+011-123456", o sea: "+", característica provincial, "-" (guión), y por último número de teléfono. En caso de ser celular, omita el "15".')],
    telefono = models.BigIntegerField(null=True)
    nacimiento = models.DateField(null=True)  #Esto hay que ponerlo en la version final. No nos importa la hora en la que nacio la persona, solo el dia.
    
    class Meta:
        permissions = (('es_recepcionista','Usuario tiene rol de recepcionista'),)

    def str(self):
        return '%s %s' % (self.first_name, self.last_name)
    
    def __str__(self):
        return self.str()

class Paciente(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, primary_key=True)
    GENERO_CHOICES = (
        (1, "Masculino"),
        (2, "Femenino"),
    )

    genero = models.PositiveSmallIntegerField(choices=GENERO_CHOICES)
    penalizado = models.BooleanField(default=False)
    fecha_despenalizacion = models.DateTimeField(verbose_name="fecha de despenalización", blank=True, null=True)
    obra_social = models.ForeignKey(ObraSocial, on_delete=models.CASCADE, blank=True, null=True)

    def get_genero(self):
        return dict(self.GENERO_CHOICES).get(self.genero)


    class Meta:
         permissions = (('es_paciente','Usuario tiene rol de paciente'),)

    def __str__(self):
        return self.user.__str__()
    
    def penalizar(self):
        self.penalizado = True
        self.fecha_despenalizacion = datetime.date.today() + timedelta(days=7)
    
    def despenalizar(self):
        self.penalizado = False

class Medico(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, primary_key=True)
    # Validator del CUIL, ídem que con el documento: validators=[RegexValidator(regex='[0-9]{2}-[0-9]{8}-[0-9]$', message='La constancia de CUIL introducida debe ser de formato "XX-XXXXXXXX-X".', code='nomatch')], 
    cuil = models.BigIntegerField(unique=True)
    especialidad = models.ForeignKey(Especialidad, on_delete=models.CASCADE)

    class Meta:
         permissions = (('es_medico','Usuario tiene rol de medico'),)

    def __str__(self):
        return self.user.__str__()
    
