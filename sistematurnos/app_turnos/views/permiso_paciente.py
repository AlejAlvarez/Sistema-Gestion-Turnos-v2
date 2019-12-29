from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import ListView, DetailView
from django.core import serializers
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.utils import timezone

from datetime import timedelta, datetime, date

from ..models import *
from app_usuarios.models import Medico, CustomUser
from ..forms import *
from app_usuarios.views.views_user import check_ownership_or_403


class ListarTurnos(PermissionRequiredMixin, ListView):
    permission_required = ('app_usuarios.es_paciente')
    model = Turno
    template_name = 'turnos/lista_turnos.html'
    context_object_name = 'lista_turnos'

    def get_queryset(self):
        """ Filtra por el usuario provisto en el request.user """
        queryset = super(ListarTurnos, self).get_queryset()
        paciente = Paciente.objects.get(pk=self.request.user.pk)
        lista_turnos = queryset.filter(paciente=paciente, estado=2)
        return lista_turnos

class VerTurno(PermissionRequiredMixin, DetailView):
    permission_required = ('app_usuarios.es_paciente')
    model = Turno
    template_name = 'turnos/informacion_turno.html'

@login_required
@permission_required('app_usuarios.es_paciente')
def buscar_turnos(request):
    
    if request.method == "POST":
        form = BuscarTurnosForm(request.POST)
        if form.is_valid():
            especialidad = form.cleaned_data.get('especialidad')
            medico = form.cleaned_data.get('medico')
            fecha = form.cleaned_data.get('fecha')
            lista_turnos = []
            if medico == None:
                lista_medicos = Medico.objects.filter(especialidad=especialidad)
                for medico in lista_medicos:
                    # Estado 1 = 'Disponible'
                    lista_turnos_medico = Turno.objects.filter(medico=medico, estado=1)
                    # Voy concatenando las listas de turnos
                    lista_turnos.extend(Turno.get_turnos_fecha(lista_turnos_medico, fecha))
                lista_turnos.sort(key=lambda turno: turno.fecha)
            else:
                # Estado 1 = 'Disponible'
                lista_turnos_medico = Turno.objects.filter(medico=medico, estado=1)
                # Consigo los turnos de una determinada fecha
                lista_turnos = Turno.get_turnos_fecha(lista_turnos_medico, fecha)
                lista_turnos.sort(key=lambda turno: turno.fecha)

            if lista_turnos:
                # Parece que esto se podría hacer con Django Cache Framework
                request.session['lista_turnos'] = serializers.serialize('json', lista_turnos)
                return redirect('app_turnos:reservar-turno')
            else:
                return HttpResponse("Lo sentimos, no se han encontrado turnos disponibles en la fecha seleccionada.")
    
    else:
        form = BuscarTurnosForm()
        return render(request, 'turnos/accion_turno.html', {'form': form, 'accion': "Buscar"})

@login_required
@permission_required('app_usuarios.es_paciente')
def reservar_turno(request):

    if not request.session['lista_turnos']:
        return HttpResponse('Debe realizar una búsqueda de turnos primero.')
    lista_turnos_id = []
    for turno in serializers.deserialize('json', request.session['lista_turnos']):
        lista_turnos_id.append(turno.object.id)
    turnos = Turno.objects.filter(id__in=lista_turnos_id)

    if request.method == "POST":
        # Aca obtengo la fila que seleccionó el paciente (o sea, el turno), y verifico que siga disponible
        # luego, se lo reservo a este paciente
        form = SeleccionarTurnoForm(turnos=turnos, data=request.POST)
        if form.is_valid():
            usuario = CustomUser.objects.get(pk=request.user.pk)
            paciente = Paciente.objects.get(user=usuario)
            if paciente.penalizado:
                if paciente.fecha_despenalizacion > datetime.date.today():
                    # Lo reboto porque todavía está penalizado
                    return HttpResponse('Usted actualmente se encuentra penalizado. \n Podrá solicitar turnos a partir del día %s' % (paciente.fecha_despenalizacion))
                else:
                    # Cumplió su condena. Lo despenalizo
                    paciente.despenalizar()
                    paciente.save()
            turno = form.cleaned_data.get('turno')
            if turno.estado == 1:
                turno.paciente = paciente
                # Cambio el estado del turno a 'Reservado'
                turno.estado = 2 
                turno.save()
            else:
                return HttpResponse("Lo sentimos, ese turno parece ya no estar disponible. \n Por favor, seleccione otro.")

            return HttpResponse("Su turno, Sr/Sra %s ha sido reservado con éxito! La fecha será %s" % (request.user, turno.fecha))
    else:
        # Renderizo la datatable con los datos de los turnos        
        form = SeleccionarTurnoForm(turnos=turnos)
        return render(request, 'turnos/accion_turno.html', {'form':form, 'accion': "Reservar"})

@login_required
@permission_required('app_usuarios.es_paciente')
def cancelar_turno(request, pk):
    
    turno = Turno.objects.get(pk=pk)
    hora_actual = timezone.now()

    # Si cancela menos de 2 horas antes
    if hora_actual + timedelta(hours=2) >= turno.fecha:
        turno.estado = 5 # Estado cancelado
        turno.save()
        turno_cancelado = TurnoCancelado.objects.create(turno=turno, fecha_cancelado=hora_actual)
        turno_cancelado.save()
        paciente.penalizado = True
        paciente.fecha_despenalizacion = timezone.now() + timedelta(days=2) # Lo penalizo por 2 días nomas porque fue copado y avisó
        paciente.save()
    else:
        turno.estado = 1 # Estado disponible
        turno.paciente = None
        turno.save()

    return redirect('app_turnos:mis-turnos')


@login_required
@permission_required('app_usuarios.es_paciente')
def ver_historial(request):

    paciente = Paciente.objects.get(pk=request.user.pk)
    turnos = Turno.objects.filter(paciente=paciente).order_by('-fecha', 'especialidad')

    return render(request, 'turnos/lista_turnos.html', lista_turnos=turnos)


