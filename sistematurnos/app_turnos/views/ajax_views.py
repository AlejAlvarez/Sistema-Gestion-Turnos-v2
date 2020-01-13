# AJAX VIEWS
from django.views.generic import View
from django.http import JsonResponse
from django.core import serializers
from ..models import Turno
from .. forms import SeleccionarTurnoForm
from app_usuarios.models import Medico
from app_informacion.models import Especialidad

class ObtenerTurnosAjax(View):
    
    def get(self,request):
        especialidad_seleccionada = request.GET.get('especialidad_seleccionada',None)
        # obtener primero los médicos por esp1ecialidad
        especialidad_medico = Especialidad.objects.get(nombre=especialidad_seleccionada)
        medicos_especialidad = Medico.objects.filter(especialidad=especialidad_medico.id)
        medicos_id = [ medico.user_id for medico in medicos_especialidad ]
        # luego obtener los turnos por médico, falta filtrarlos por medico
        # estado 1 = Disponible
        turnos_especialidad = Turno.get_turnos_weeks_ahead(estado=1).filter(medico_id__in=medicos_id)
        # se crea un objeto Json para enviar de nuevo al cliente)
        turnos_as_json = []
        # objeto json para los formularios de turno
        for turno in turnos_especialidad:
            turnos_as_json.append(turno.as_json())
        data = turnos_as_json
        return JsonResponse(data,safe=False)
