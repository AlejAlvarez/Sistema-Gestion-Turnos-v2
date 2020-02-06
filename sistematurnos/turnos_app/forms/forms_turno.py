from django import forms
from django.forms import models
from ..models import *
import datetime
from flatpickr import DatePickerInput, TimePickerInput, DateTimePickerInput

# formularios que pueden ser reutilizados por usuarios con distintos roles

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

class SeleccionarEspecialidadForm(forms.Form):
    especialidades = forms.ModelChoiceField(
        queryset = Especialidad.objects.none(),
        empty_label = "Seleccione una especialidad",
    )

    def __init__(self,*args,**kwargs):
        especialidades_queryset = kwargs.pop('especialidades')
        super(SeleccionarEspecialidadForm,self).__init__(*args,**kwargs)
        if(especialidades_queryset):
            self.set_especialidades(especialidades_queryset)

    def set_especialidades(self,especialidades):
        self.fields['especialidades'].queryset = especialidades


#retorna los turnos ordenados por id/pk
class SeleccionarTurnoForm(forms.Form):

    turnos = forms.ModelChoiceField(
        queryset=Turno.objects.none(),
        empty_label=None,
        widget=forms.RadioSelect(),
    )
    def __init__(self, *args, **kwargs):
        qs = kwargs.pop('turnos')
        super(SeleccionarTurnoForm, self).__init__(*args, **kwargs)
        self.fields['turnos'].queryset = qs
        self.turnos_informacion = list(qs)
        # según la documentación, la mejor manera de hacerlo es a través de una clase que herede de ésta, y reescribiendo el método
        self.fields['turnos'].label_from_instance = lambda obj: obj.fecha.time



class BuscarEspecialidadForm(forms.Form):
    especialidad = forms.ModelChoiceField(
        queryset = Especialidad.objects.all(),
        required = True,
    )
    fecha = forms.DateField(widget=DatePickerInput(
        options = {  
            # flatpickr options
            "dateFormat": "d/m/Y",
            "minDate": str(datetime.date.today()),
        }).start_of(datetime.date.today())
    )

class BuscarTurnosByMedicoForm(forms.Form):
    medico = forms.ModelChoiceField(
        queryset=Medico.objects.none(),
        required=True,
    )

    def set_medicos(self,medicos):
        self.fields['medico'].queryset = medicos


class AtenderTurnoForm(forms.Form):
    diagnostico = forms.CharField()