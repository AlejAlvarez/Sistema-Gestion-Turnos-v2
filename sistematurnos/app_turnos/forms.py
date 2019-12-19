from django import forms
from django.forms import models
import datetime

from .models import Turno, DIA_CHOICES
from app_usuarios.models import Medico
from app_informacion.models import Especialidad

class TurnoForm(forms.Form):
    dias_atencion = forms.MultipleChoiceField(
        label="Días de atención",
        widget=forms.CheckboxSelectMultiple,
        choices=DIA_CHOICES,
    )
    hora_inicio = forms.TimeField(label="Hora de inicio")
    hora_fin = forms.TimeField(label="Hora de finalización")
    duracion_turno = forms.IntegerField()
    sobreturnos = forms.BooleanField(label="Acepta sobreturnos?", required=False)

class BuscarTurnosForm(forms.Form):
    especialidad = forms.ModelChoiceField(
        queryset=Especialidad.objects.all()
    )
    medico = forms.ModelChoiceField(
        queryset=Medico.objects.all(),
        required=False
    )
    fecha = forms.DateField(initial=datetime.date.today, widget=forms.SelectDateWidget())

class SeleccionarTurnoForm(forms.Form):
    turno = forms.ModelChoiceField(
        queryset=Turno.objects.none(),
        widget=forms.RadioSelect
    )

    def __init__(self, *args, **kwargs):
        qs = kwargs.pop('turnos')
        super(SeleccionarTurnoForm, self).__init__(*args, **kwargs)
        self.fields['turno'].queryset = qs

class AtenderTurnoForm(forms.Form):
    diagnostico = forms.CharField()


