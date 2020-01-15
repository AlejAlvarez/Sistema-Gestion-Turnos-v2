from django.db import models
from django.utils import timezone
from datetime import datetime, timedelta
from app_usuarios.models import Medico, Paciente

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
    
    @staticmethod
    def historial(paciente):
        turnos = Turno.objects.filter(paciente=paciente).order_by('-fecha', 'medico')

        return turnos

    # por defecto va a retornar dos semanas
    @staticmethod 
    def get_turnos_weeks_ahead(estado,number_of_weeks=2):
        time_dt = timedelta(weeks=number_of_weeks)
        startdate = datetime.now()
        enddate = datetime.now() + time_dt
        if estado:
            lista_turnos = Turno.objects.filter(estado=estado,fecha__range=[startdate,enddate])
        else: 
            lista_turnos = Turno.objects.filter(fecha__range=[startdate,enddate])
        return lista_turnos

    def as_json(self):
        return dict({
            'pk':self.pk,
            'fecha':self.fecha.strftime('%d-%m-%Y'),
            'hora':self.fecha.strftime('%H:%M'),
            'paciente':self.paciente.__str__(),
            'medico':self.medico.__str__(),
            'es_sobreturno':self.es_sobreturno,
            'prioridad':self.prioridad
        })

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