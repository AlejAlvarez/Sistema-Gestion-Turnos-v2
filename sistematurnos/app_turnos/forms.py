from django import forms
from django.forms import models, ModelForm
import datetime
from .models import Turno, DIA_CHOICES
from app_usuarios.models import Medico
from app_informacion.models import Especialidad
from django.utils.dateparse import parse_datetime
from django.utils.timezone import is_aware,make_aware

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
    # esto en realidad tiene que ser el conjunto de médicos disponibles por especialidad
    medico = forms.ModelChoiceField(
        queryset=Medico.objects.all(),
        required=False
    )
    fecha = forms.DateField(initial=datetime.date.today, widget=forms.SelectDateWidget())

# retorna los turnos ordenados por id/pk
class SeleccionarTurnoForm(forms.Form):
    turno = forms.ModelChoiceField(
        queryset=Turno.objects.none(),
        empty_label=None,
        widget=forms.RadioSelect
    )
    def __init__(self, *args, **kwargs):
        qs = kwargs.pop('turnos')
        super(SeleccionarTurnoForm, self).__init__(*args, **kwargs)
        self.fields['turno'].queryset = qs
        self.turnos_informacion = list(qs)
        self.fields['turno'].label_from_instance = lambda obj: "Turno %s" % obj.id

class AtenderTurnoForm(forms.Form):
    diagnostico = forms.CharField()

class SeleccionarEspecialidadForm(forms.Form):
    especialidades = forms.ModelChoiceField(
        queryset = Especialidad.objects.none(),
        # empty_label = None,
    )

    def __init__(self,*args,**kwargs):
        especialidades_queryset = kwargs.pop('especialidades')
        super(SeleccionarEspecialidadForm,self).__init__(*args,**kwargs)
        if(especialidades_queryset):
            self.set_especialidades(especialidades_queryset)
            set_all_widgets_bootstrap_class(self.fields)

    def set_especialidades(self,especialidades):
        self.fields['especialidades'].queryset = especialidades

class CompletarReservaForm(forms.Form):

    turno_id = forms.DecimalField(
        label='',
        widget=forms.NumberInput(
            attrs = {'name':'id_turno','hidden':True,'readonly':True})
    )
    # va a contener el dni
    dni_paciente = forms.DecimalField(
        label='Paciente',
        widget=forms.NumberInput(attrs = {'name':'dni_paciente'})
    )
    especialidad = forms.CharField(
        label="Especialidad",
        widget=forms.TextInput(
            attrs={'readonly':True, 'name':'especialidad'})
    )
    medico = forms.CharField(
        label='Médico',
        widget=forms.TextInput(
            attrs = {'readonly':True,'name':'medico'})
    )
    #fecha = forms.DateTimeField(
    #    label='Fecha',
    #    input_formats=['%d-%m-%Y %H:%M',],
    #    widget=forms.TextInput(attrs={'readonly':True})
    #)
    date = forms.DateField(
        label="Fecha",
        input_formats=['%d-%m-%Y'],
        widget=forms.DateInput(attrs={'readonly':True})
    )
    time = forms.TimeField(
        label='Hora',
        input_formats=['%H:%M',],
        widget=forms.TimeInput(attrs={'readonly':True})
    )
    def __init__(self,*args,**kwargs):
        turno_instance = None
        if 'turno' in kwargs:
            turno_instance = kwargs.pop('turno')
        super(CompletarReservaForm,self).__init__(*args,**kwargs)
        if(turno_instance):
            self.set_turno_fields(turno_instance)
        set_all_widgets_bootstrap_class(self.fields)

    def set_turno_fields(self,turno):
        medico_turno = Medico.objects.get(user_id=turno.medico)
        self.fields['turno_id'].widget.attrs['value'] = turno.id
        self.fields['medico'].widget.attrs['value'] = medico_turno
        self.fields['especialidad'].widget.attrs['value'] = medico_turno.especialidad
        self.fields['date'].widget.attrs['value'] = turno.fecha.strftime('%d-%m-%Y')
        self.fields['time'].widget.attrs['value'] = turno.fecha.strftime('%H:%M')

def set_all_widgets_bootstrap_class(form_fields):
    for field in form_fields:
        form_fields[field].widget.attrs.update({
                'class': 'form-control'
            })