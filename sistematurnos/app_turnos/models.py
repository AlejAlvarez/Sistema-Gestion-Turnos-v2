from django.db import models
from django.utils import timezone

from app_usuarios.models import Medico, Paciente

class Turno(models.Model):
    ESTADO_CHOICES = (
        (1, "disponible"),
        (2, "pendiente"),
        (3, "aceptado"),
        (4, "cancelado"),
        (5, "atendido"),
    )

    estado = models.PositiveSmallIntegerField(choices=ESTADO_CHOICES)
    fecha = models.DateTimeField()
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    medico = models.ForeignKey(Medico, on_delete=models.CASCADE)
    is_sobreturno = models.BooleanField(default=False)
    prioridad = models.PositiveSmallIntegerField(blank=True, null=True)

class TurnoCancelado(Turno):
    fecha_cancelado = models.DateTimeField(auto_now_add=True)

class TurnoAtendido(Turno):
    diagnostico = models.TextField()