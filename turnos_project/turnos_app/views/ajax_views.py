from django.views.generic import View
from django.http import JsonResponse
from django.core import serializers
from django.shortcuts import render
from django.contrib.auth.mixins import PermissionRequiredMixin
import json
from datetime import timedelta
from django.utils import timezone
from ..models import *
from ..forms.forms_turno import BuscarEspecialidadForm, BuscarTurnosByMedicoForm, SeleccionarTurnoForm


def get_paciente_by_documento(documento):
    try:
        user = CustomUser.objects.get(documento=documento)
        if (user.has_perm('turnos_app.es_paciente')):
            # checkear si es paciente
            paciente = Paciente.objects.get(pk=user.id)
            return paciente
        else: 
            return None
    except CustomUser.DoesNotExist:
        return None


# PACIENTE AJAX VIEWS

class BuscarMedicosAjax(PermissionRequiredMixin,View):

    permission_required = ('turnos_app.es_paciente')

    """ recibe como parametro la especialidad y la fecha y 
        retorna el formulario con todos los medicos disponibles a la fecha """
    def get(self,request):
        if request.is_ajax():
            # should check if form is valid
            fecha = request.GET['fecha']
            especialidad = request.GET['especialidad']
            medicos_especialidad = Medico.objects.filter(especialidad=especialidad)
            diccionario_medico = {}
            data = {}
            i = 0
            for medico in medicos_especialidad:
                diccionario_medico = {
                    'id':medico.pk,
                    'nombre': medico.user.first_name + " " + medico.user.last_name,
                }
                data.update({i:diccionario_medico})
                i += 1
            return JsonResponse(data)
    
class BuscarTurnosAjax(PermissionRequiredMixin,View):

    permission_required = ('turnos_app.es_paciente')

    """ recibe como parametro la especialidad y la fecha y 
        retorna el formulario con todos los medicos disponibles a la fecha """
    def get(self,request):
        if request.is_ajax():
            # necesario para extraer la fecha
            especialidad_form = BuscarEspecialidadForm(request.GET)
            if (especialidad_form.is_valid()): 
                fecha = especialidad_form.cleaned_data.get('fecha')
            medico = Medico.objects.get(user_id=request.GET['medico'])
            # Estado 1 = 'Disponible'
            lista_turnos_medico = Turno.objects.filter(medico=medico, estado=1)
            # Consigo los turnos de una determinada fecha
            lista_turnos = Turno.get_turnos_fecha(lista_turnos_medico, fecha)
            lista_turnos_id = []
            for turno in lista_turnos:
                lista_turnos_id.append(turno.id)
            turnos = Turno.objects.filter(id__in=lista_turnos_id)

            # retorna el template
            turnos_form = SeleccionarTurnoForm()
            turnos_form.set_turnos(turnos=turnos)
            context = {'turnos_form':turnos_form}
            return render(request,'paciente/tabla_turnos_form.html',context)
# MEDICO AJAX VIEWS


# ADMIN AJAX VIEWS