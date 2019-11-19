from django import forms
from django.forms import models

from .models import Turno, DIA_CHOICES

class TurnoForm(forms.Form):
    dias_atencion = forms.MultipleChoiceField(
        label="Días de atención",
        widget=forms.CheckboxSelectMultiple,
        choices=DIA_CHOICES,
    )
    hora_inicio = forms.TimeField(label="Hora de inicio")
    hora_fin = forms.TimeField(label="Hora de finalización")
    duracion_turno = forms.IntegerField() # No se estaría mostrando en el template
    sobreturnos = forms.BooleanField(label="Acepta sobreturnos?", required=False)
