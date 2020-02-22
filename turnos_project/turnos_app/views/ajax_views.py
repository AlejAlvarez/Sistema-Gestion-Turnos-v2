from django.views.generic import View
from django.http import JsonResponse
from django.core import serializers
from django.shortcuts import render
from django.contrib.auth.mixins import PermissionRequiredMixin
import json
import datetime
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
            turnos_form = SeleccionarTurnoForm(turnos=turnos)
            context = {'turnos_form':turnos_form}
            return render(request,'paciente/tabla_turnos_form.html',context)

# RECECEPCIONISTA AJAX VIEWS

class ObtenerPacienteAjax(PermissionRequiredMixin,View):

    template_name = 'recepcionista/tarjeta_paciente.html'
    permission_required = ('turnos_app.es_recepcionista')

    def get(self,request):
        if request.is_ajax():
            if(request.GET['documento']):
                paciente = get_paciente_by_documento(request.GET['documento'])
                if paciente is not None:
                    return render(request,self.template_name,{'paciente':paciente})
                else:
                    return render(request,self.template_name,{})
            else:
                return render(request,self.template_name,{})

class ConsultarTurnosEspecialidadAjax(PermissionRequiredMixin,View):

    permission_required = ('turnos_app.es_recepcionista')

    def get(self,request):
        if request.is_ajax():
            paciente = get_paciente_by_documento(request.GET['documento'])
            if paciente is None:
                return render(request,'recepcionista/buscar_turnos.html',{})
            especialidad = request.GET['especialidades']
            # obtener los médicos por especialidad
            medicos_especialidad = Medico.objects.filter(especialidad=especialidad)
            medicos_id = []
            # creo una lista de ids con los medicos obtenidos
            for medico in medicos_especialidad:
                medicos_id.append(medico.user_id)
            # obtengo los turnos por un rango de fecha, en este caso 2 semanas y Estado = 1: Disponible
            time_dt = timedelta(weeks=2)
            day_dt = timedelta(days=1)
            # debería filtrar por fecha en lugar de fecha y hora
            startdate = datetime.datetime.now() - day_dt
            # debería filtrar por fecha en lugar de fecha y hora
            enddate = datetime.datetime.now() + time_dt
            turnos = Turno.objects.filter(medico_id__in=medicos_id,estado=1,fecha__range=[startdate,enddate]).order_by('fecha')
            turno_form = SeleccionarTurnoForm(turnos=turnos)
            context = {
                'turnos_form':turno_form
            }
            return render(request,'recepcionista/buscar_turnos.html',context)

# MEDICO AJAX VIEWS


# ADMIN AJAX VIEWS