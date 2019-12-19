from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import ListView
from django.core import serializers
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin 

from datetime import timedelta, datetime, date

from ..models import *
from app_usuarios.models import Medico, CustomUser
from ..forms import *
from app_usuarios.views.views_user import check_ownership_or_403


# Funcion lambda utilizada para calcular los días de los turnos
onDay = lambda dt, day: dt + timedelta(days=(day - dt.weekday())%7)

@login_required
@permission_required('app_usuarios.es_medico')
def crear_turnos(request):

    if request.method == 'POST':
        form = TurnoForm(request.POST)
        if form.is_valid():
            dias        = form.cleaned_data.get('dias_atencion')
            hora_inicio = form.cleaned_data.get('hora_inicio')
            hora_fin    = form.cleaned_data.get('hora_fin')
            duracion    = form.cleaned_data.get('duracion_turno')
            sobreturnos = form.cleaned_data.get('sobreturnos')
            usuario     = CustomUser.objects.get(pk=request.user.pk)
            medico      = Medico.objects.get(user=usuario)

            # Esto corrobora que no se estén superponiendo horarios laborales ya creados
            for dia in dias:
                try:
                    dia_laboral = DiaLaboral.objects.get(medico=medico, dia=dia)
                    print(dia_laboral)
                    horarios_laborales_existentes = HorarioLaboral.objects.filter(dia_laboral=dia_laboral)
                    if horarios_laborales_existentes:
                        for horario in horarios_laborales_existentes:
                            if(hora_inicio >= horario.hora_inicio and hora_inicio < horario.hora_fin) or (hora_fin > horario.hora_inicio and hora_fin <= horario.hora_fin):
                                return HttpResponse("Error, se están superponiendo horarios.")
                except DiaLaboral.DoesNotExist:
                    print("Dia ", dia, " no se encuentra creado actualmente.")
            
            # Creamos los turnos en cada dia, con los distintos horarios posibles.
            for dia in dias:
                fecha_laboral = onDay(date.today(), int(dia))
                dia_laboral = DiaLaboral.objects.get_or_create(medico=medico, dia=dia)[0]
                print(dia_laboral)
                horario_laboral = HorarioLaboral.objects.create(dia_laboral=dia_laboral, hora_inicio=hora_inicio, hora_fin=hora_fin, sobreturnos=sobreturnos)
                mes_actual = date.today().month
                while fecha_laboral.month == mes_actual:
                    hora_turno = datetime.datetime.combine(fecha_laboral, hora_inicio)
                    while hora_turno.time() <= hora_fin:
                        turno = Turno()
                        turno.medico = medico
                        turno.estado = 1 # Estado 1 = 'disponible'
                        fecha_atencion = datetime.datetime.combine(fecha_laboral, hora_turno.time())
                        print("Dia laboral: ", fecha_laboral)
                        print("Fecha de atencion: ", fecha_atencion)
                        turno.fecha  = fecha_atencion
                        turno.save()
                        hora_turno = hora_turno + timedelta(minutes=duracion)
                    print("Salió del loop de hora_turno")
                    fecha_laboral = onDay(fecha_laboral + timedelta(days=7), 1)
                print("Termino de cargar turnos para el mes")
            
            return render(request, 'turnos/lista_turnos.html', {'lista_turnos': Turno.objects.filter(medico=medico)})
    else:
        form = TurnoForm()
        
    return render(request, 'turnos/crear_turnos.html', {'form': form})

@login_required
@permission_required('app_usuarios.es_medico')
def seleccionar_turno_a_atender(request):
    lista_turnos = Turno.get_turnos_fecha(Turno.objects.filter(estado=3), datetime.date.today())
    usuario = CustomUser.objects.get(pk=request.user.pk)
    medico = Medico.objects.get(user=usuario)
    if lista_turnos:
        lista_turnos_id = [turno.id for turno in lista_turnos]
        turnos = Turno.objects.filter(id__in=lista_turnos_id, medico=medico)
    else: 
        return HttpResponse('Aún no han sido confirmado turnos para el día de hoy.')

    if request.method == 'POST':
        form = SeleccionarTurnoForm(turnos=turnos, data=request.POST)
        if form.is_valid():
            turno = form.cleaned_data.get('turno')
            return HttpResponseRedirect('/turnos/atender-turno/%s/' % (turno.id))
    else:
        form = SeleccionarTurnoForm(turnos=turnos)
        return render(request, 'turnos/accion_turno.html', {'form':form, 'accion':"Seleccionar"})

@login_required
@permission_required('app_usuarios.es_medico')
def atender_turno(request, turno_id):
    if request.method == 'POST':
        form = AtenderTurnoForm(request.POST)
        if form.is_valid():
            turno = Turno.objects.get(id=turno_id)
            turno.estado = 4 # Estado atendido
            turno.save()
            turno_atendido = TurnoAtendido()
            turno_atendido.turno = turno
            turno_atendido.diagnostico = form.cleaned_data.get('diagnostico')
            turno_atendido.save()
            return redirect('app_turnos:seleccionar-turno-a-atender')
    else:
        form = AtenderTurnoForm()
        return render(request, 'turnos/accion_turno.html', {'form':form, 'accion':"Seleccionar"})

