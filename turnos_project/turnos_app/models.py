from django.db import models
from django.db.models import Q
from django.contrib.auth.models import AbstractUser
import datetime
from datetime import timedelta
from django.utils import timezone

# Create your models here.

# USUARIOS MODELS 
  
class CustomUser(AbstractUser):
    # Validator del documento, ni idea si funciona: validators=[RegexValidator(regex='[0-9]{8}$', message='El documento introducido debe ser de 8 dígitos', code='nomatch')], 
    documento = models.BigIntegerField(unique=True, null=True)
    domicilio = models.CharField(max_length=100, null=True)
    # Validator del telefono, ídem que con el documento: validators=[RegexValidator(regex='+[0-9]{2,4}-[0-9]{6}$', message='Introduzca un numero de teléfono válido, con la forma "+011-123456", o sea: "+", característica provincial, "-" (guión), y por último número de teléfono. En caso de ser celular, omita el "15".')],
    telefono = models.BigIntegerField(null=True)
    nacimiento = models.DateField(null=True)  #Esto hay que ponerlo en la version final. No nos importa la hora en la que nacio la persona, solo el dia.
    
    class Meta:
        permissions = (('es_recepcionista','Usuario tiene rol de recepcionista'),
                        ('es_administrador','Usuario tiene rol de administrador'),
                        ('es_paciente', 'Usuario tiene rol de paciente'),
                        ('es_medico', 'Usuario tiene rol de medico'),)

    def str(self):
        return '%s %s' % (self.first_name, self.last_name)
    
    def __str__(self):
        return self.str()

class ObraSocial(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    pacientes = models.IntegerField(default=0)

    def __str__(self):
        return self.nombre


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

    def __str__(self):
        return self.user.__str__()
    
    def penalizar(self):
        self.penalizado = True
        self.fecha_despenalizacion = datetime.date.today() + timedelta(days=7)
    
    def despenalizar(self):
        self.penalizado = False

    """ se filtran por estado y fecha, la hora no se tiene en cuenta, porque puede ser confirmado excediendo el la hora """ 
    def get_turnos_pendientes(self):
        # estado 2 = Reservado y 3 = Confirmado
        today = datetime.date.today()
        lista_turnos = Turno.objects.filter(Q(paciente=self),Q(estado=2)|Q(estado=3)).order_by('-pk')
        lista_retorno = [turno for turno in lista_turnos if (turno.fecha.date() >= today)]
        return lista_retorno 

class Especialidad(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    medicos = models.IntegerField(default=0)

    def __str__(self):
        return self.nombre

class Medico(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, primary_key=True)
    # Validator del CUIL, ídem que con el documento: validators=[RegexValidator(regex='[0-9]{2}-[0-9]{8}-[0-9]$', message='La constancia de CUIL introducida debe ser de formato "XX-XXXXXXXX-X".', code='nomatch')], 
    cuil = models.BigIntegerField(unique=True)
    especialidad = models.ForeignKey(Especialidad, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.__str__()

# TURNOS MODELS

ESTADO_CHOICES = (
    (1, "Disponible"),
    (2, "Reservado"),
    (3, "Confirmado"),
    (4, "Atendido"),
    (5, "Cancelado"),
)

class Turno(models.Model):
    estado        = models.PositiveSmallIntegerField(choices=ESTADO_CHOICES)
    fecha         = models.DateTimeField()
    paciente      = models.ForeignKey(Paciente, on_delete=models.CASCADE, null=True,blank=True)
    medico        = models.ForeignKey(Medico, on_delete=models.CASCADE)
    es_sobreturno = models.BooleanField(default=False)
    prioridad     = models.PositiveSmallIntegerField(blank=True, null=True)

    def get_estado(self):
        return dict(ESTADO_CHOICES).get(self.estado)
    
    def __str__(self):
        return '%s, %s' % (self.fecha, self.medico)

    @staticmethod
    def get_turnos_fecha(turnos, fecha):
        lista_turnos = []
        for turno in turnos:
            if turno.fecha.date() == fecha:
                lista_turnos.append(turno)
        return lista_turnos
    
    # va a retornar sólamente los turnos cancelados y atendidos
    @staticmethod
    def historial(paciente):
        try:
            turnos = Turno.objects.get(Q(paciente=paciente),Q(estado=4)|Q(estado=5)).order_by('-fecha', 'medico')
        except Turno.DoesNotExist:
            turnos = None
        return turnos

    # por defecto va a retornar dos semanas
    @staticmethod 
    def get_turnos_weeks_ahead(number_of_weeks=2):
        time_dt = timedelta(weeks=number_of_weeks)
        startdate = datetime.datetime.now()
        enddate = datetime.datetime.now() + time_dt 
        lista_turnos = Turno.objects.filter(fecha__range=[startdate,enddate])
        return lista_turnos

class TurnoCancelado(models.Model):
    turno = models.OneToOneField(Turno, on_delete=models.CASCADE, primary_key=True)
    fecha_cancelado = models.DateTimeField(auto_now_add=True)

    def debe_penalizar(self):
        if self.fecha_cancelado + timedelta(hours=24) >= self.turno.fecha:
            return True
        return False

class TurnoAtendido(models.Model):
    turno = models.OneToOneField(Turno, on_delete=models.CASCADE, primary_key=True)
    diagnostico = models.TextField()

DIA_CHOICES = [
    (0, "Lunes"),
    (1, "Martes"),
    (2, "Miércoles"),
    (3, "Jueves"),
    (4, "Viernes"),
    (5, "Sábado"),
    (6, "Domingo"),
]

class DiaLaboral(models.Model):
    dia    = models.PositiveSmallIntegerField(choices=DIA_CHOICES)
    medico = models.ForeignKey(Medico, on_delete=models.CASCADE)

    def get_dia(self):
        return dict(DIA_CHOICES).get(self.dia)

    def __str__(self):
        return '%s, %s' % (self.get_dia(), self.medico)


class HorarioLaboral(models.Model):
    dia_laboral = models.ForeignKey(DiaLaboral, on_delete=models.CASCADE)
    hora_inicio = models.TimeField()
    hora_fin    = models.TimeField()
    sobreturnos = models.BooleanField(default=False)

    def acepta_sobreturnos(self):
        return sobreturnos
    
    def __str__(self):
        return '%s, %s, %s' % (self.dia_laboral, self.hora_inicio, self.hora_fin)
