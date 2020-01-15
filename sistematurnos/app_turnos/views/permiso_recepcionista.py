from django.shortcuts import render, redirect
from django.urls import reverse,reverse_lazy
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import ListView
from django.core import serializers
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.utils import timezone
from django.utils.timezone import is_aware,make_aware
from datetime import timedelta, datetime, date
#borrar despues
from django.core import serializers

from ..models import *
from app_usuarios.models import Medico, CustomUser
from app_informacion.models import Especialidad
from ..forms import *
from app_usuarios.views.views_user import check_ownership_or_403
from django.contrib.auth.models import Permission

@login_required
@permission_required('app_usuarios.es_recepcionista')
def gestionar_turnos(request):
    lista_turnos = Turno.get_turnos_fecha(Turno.objects.filter(estado=2), datetime.date.today())
    if lista_turnos:
        lista_turnos_id = [turno.id for turno in lista_turnos]
        # turnos están ordenados por id/pk
        turnos = Turno.objects.filter(id__in=lista_turnos_id)
    else: 
        return render(request, 'turnos/gestionar_turnos.html')

    if request.method == 'POST':
        form = SeleccionarTurnoForm(turnos=turnos, data=request.POST)
        print('Entro al if POST')
        print(form)
        if form.is_valid():
            print("El form es valido")
            if 'confirmar' in request.POST:
                print("Entro al confirmar")
                turno = form.cleaned_data.get('turno')
                turno.estado = 3 # Cambio el estado a 'Confirmado'
                turno.save()
                
            elif 'cancelar' in request.POST:
                print("Entro al cancelar")
                turno = form.cleaned_data.get('turno')
                print(turno)
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
            
        form = SeleccionarTurnoForm(turnos=turnos)
        return render(request, 'turnos/gestionar_turnos.html', {'form':form})
    else:
        form = SeleccionarTurnoForm(turnos=turnos)
        return render(request, 'turnos/gestionar_turnos.html', {'form':form})

@login_required
@permission_required('app_usuarios.es_recepcionista')
def reservar_turnos(request):

    if request.method == "POST":
        especialidades_form = SeleccionarEspecialidadForm(especialidades=Especialidad.objects.all(),data=request.POST)
        if  ("reservar" in request.POST):
            turno_id = request.POST.get('turno')
            # lógica para reservar turno
            return redirect('app_turnos:completar-reserva',turno_id=turno_id)
        elif (especialidades_form.is_valid()):
            especialidad_seleccionada = especialidades_form.cleaned_data.get('especialidades')
            # obtener primero los médicos por esp1ecialidad
            medicos_especialidad = Medico.objects.filter(especialidad=especialidad_seleccionada)
            medicos_id = [
                medico.user_id for medico in medicos_especialidad
            ]
            # luego obtener los turnos por médico, falta filtrarlos por medico
            turnos_especialidad = Turno.get_turnos_weeks_ahead(estado=1).filter(medico_id__in=medicos_id)
            return render(request,"usuarios/recepcionista/reservar_turnos.html",{'especialidad_form':especialidades_form})    
            
    else:
        user = request.user
        permissions = Permission.objects.filter(user=user)
        print("PERMISOS USUARIOS: ",permissions[0].codename)
        especialidades = Especialidad.objects.all()
        especialidades_form = SeleccionarEspecialidadForm(especialidades=especialidades)
        return render(request,'usuarios/recepcionista/reservar_turnos.html',{'especialidad_form':especialidades_form})

def completar_reserva(request,turno_id):
        turno_reservado = Turno.objects.get(id=turno_id)
        turno_reserva_form = CompletarReservaForm(turno=turno_reservado)
        if request.method == "GET":
            return render(request,'usuarios/recepcionista/completar_reserva.html',{'form':turno_reserva_form})
        else:
            #<input type="text" name="fecha" value="2020-01-11 20:39:06" required="" id="id_fecha">
            # POST method 
            form = CompletarReservaForm(data=request.POST)
            if(form.is_valid()):
                turno = Turno.objects.get(id=form.cleaned_data.get('turno_id'))
                # estado 2 = reservado
                turno.estado = 2
                #turno.paciente = Paciente.objects.get(dni = dni)
                turno.save()
                return HttpResponse("Turno Reservado con éxito titán")
            else:
                return render(request,'usuarios/recepcionista/completar_reserva.html',{'form':form})