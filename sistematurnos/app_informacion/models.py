from django.db import models

# DEPENDENCIA CIRCULAR CON MEDICO, SE PUEDE HACER UNA app_horarios?

#from app_usuarios.models import Medico

# class DiaLaboral(models.Model):
#     DIA_CHOICES = (
#         (1, 'Lunes'),
#         (2, 'Martes'),
#         (3, 'Miercoles'),
#         (4, 'Jueves'),
#         (5, 'Viernes'),
#         (6, 'Sabado'),
#         (7, 'Domingo'),
#     )
# 
#     dia = models.PositiveSmallIntegerField(choices=DIA_CHOICES)
#     medico = models.ForeignKey(Medico, on_delete=models.CASCADE)
# 
# class HorarioLaboral(models.Model):
#     hora_inicio = models.TimeField()
#     hora_fin = models.TimeField()
#     dia_laboral = models.ForeignKey(DiaLaboral, on_delete=models.CASCADE)

class ObraSocial(models.Model):
    nombre = models.CharField(max_length=100)

class Especialidad(models.Model):
    nombre = models.CharField(max_length=100)
