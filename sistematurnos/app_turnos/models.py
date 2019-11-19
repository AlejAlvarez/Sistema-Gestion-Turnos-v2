from django.db import models
from django.utils import timezone

from app_usuarios.models import Medico, Paciente

class Turno(models.Model):
    ESTADO_CHOICES = (
        (1, "disponible"),
        (2, "reservado"),
        (3, "confirmado"),
        (4, "atendido"),
        (5, "cancelado"),
    )

    estado        = models.PositiveSmallIntegerField(choices=ESTADO_CHOICES)
    fecha         = models.DateTimeField()
    paciente      = models.ForeignKey(Paciente, on_delete=models.CASCADE, null=True)
    medico        = models.ForeignKey(Medico, on_delete=models.CASCADE)
    es_sobreturno = models.BooleanField(default=False)
    prioridad     = models.PositiveSmallIntegerField(blank=True, null=True)

class TurnoCancelado(models.Model):
    turno = models.OneToOneField(Turno, on_delete=models.CASCADE, primary_key=True)
    fecha_cancelado = models.DateTimeField(auto_now_add=True)

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

class HorarioLaboral(models.Model):
    dia_laboral = models.ForeignKey(DiaLaboral, on_delete=models.CASCADE)
    hora_inicio = models.TimeField()
    hora_fin    = models.TimeField()
    sobreturnos = models.BooleanField(default=False)

    def acepta_sobreturnos(self):
        return sobreturnos