from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import ListView
from django.core import serializers
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.utils import timezone

from datetime import timedelta, datetime, date

from ..models import *
from app_usuarios.models import Medico, CustomUser
from ..forms import *
from app_usuarios.views.views_user import check_ownership_or_403


@login_required
@permission_required('app_usuarios.es_recepcionista')
def gestionar_turnos(request):
    lista_turnos = Turno.get_turnos_fecha(Turno.objects.filter(estado=2), datetime.date.today())
    if lista_turnos:
        lista_turnos_id = [turno.id for turno in lista_turnos]
        turnos = Turno.objects.filter(id__in=lista_turnos_id)
    else: 
        return HttpResponse('No existen turnos reservados para el día de hoy.')

    if request.method == 'POST':
        form = SeleccionarTurnoForm(turnos=turnos, data=request.POST)
        print('Entro al if POST')
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

