from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.urls import reverse_lazy
from django.views.generic import ListView
from django.views.generic.edit import CreateView, UpdateView 
from django.views import View
from django.core import serializers
from django.contrib import messages
from django.utils.timezone import make_aware
from django.utils import timezone

from ..models import *
from .views_usuario import *
from ..forms.user_forms import CustomUserChangeForm
from ..forms.forms_turno import SeleccionarEspecialidadForm, AtenderTurnoForm, TurnoForm
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import Permission
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login
from datetime import timedelta, datetime, date

from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response

MEDICO_PERMISSION = 'turnos_app.es_medico' 
MEDICO_LOGIN_URL = '/medico/login/'

class LoginMedicoView(View):

    template_name = 'medico/login.html'
    success_url = 'index-medico'
    
    # loguea al medico
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.has_perm(MEDICO_PERMISSION):
            return redirect(self.success_url)
        else:
            auth_form = AuthenticationForm()
            context = {
                'auth_form':auth_form,
            }
            return render(request,self.template_name,context)

    def post(self, request, *args, **kwargs):
        # get auth form and validate
        auth_form = AuthenticationForm(data=request.POST)
        context = {
            'auth_form': auth_form,
            'error_message':'',
        }        
        if auth_form.is_valid():
            username = auth_form.cleaned_data['username']
            password = auth_form.cleaned_data['password']
            user = authenticate(username=username,password=password)
            if user is not None:
                # se comprueba que tenga el permiso necesario para ingresar
                if (user.has_perm('turnos_app.es_medico') and not(user.has_perm('turnos_app.is_staff'))):
                    login(request,user)
                    next = request.session.get('next', None)
                    if next:
                        return redirect(next)    
                    return redirect(self.success_url)
                else:
                    messages.info(request,'No tiene permiso para acceder')
                    return render(request,self.template_name,context)
            messages.info(request,'No tiene permiso para acceder')
            return render(request,self.template_name,context)
        else:
            messages.error(request,'Nombre de Usuario o Contraseña Incorrecto')
            return render(request,self.template_name,context)
            
@login_required(login_url='/medico/login/')
@permission_required('turnos_app.es_medico')
# muestra la página de inicio una vez que se loguea el medico
def index_medico(request):
    pk_medico = request.user.pk
    medico_logueado = CustomUser.objects.get(pk=pk_medico)
    perfil_medico = Medico.objects.get(user=medico_logueado)
    #informacion_form = MedicoInformationForm(instance=medico_logueado)
    """ obtiene todos los turnos a partir de la hora y de 2 semanas en adelante """
    context = {'medico':medico_logueado, 'perfil_medico':perfil_medico}
    return render(request,'medico/index.html', context)


class ListarTurnosConfirmadosView(PermissionRequiredMixin, ListView):

    login_url = MEDICO_LOGIN_URL
    permission_required = ('turnos_app.es_medico')
    model = Turno
    paginate_by = 10
    template_name = 'medico/turnos_confirmados.html'
    
    def get_context_data(request, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        medico = request.request.user.medico
        turnos_confirmados = Turno.objects.filter(estado=3, medico=medico).order_by('-prioridad', 'fecha')
        context['turnos_confirmados'] = turnos_confirmados
        context['medico'] = medico
        return context

class GetMoreTurnosConfirmadosAjax(PermissionRequiredMixin, View):

    login_url = MEDICO_LOGIN_URL
    template_name = "medico/get_mas_turnos.html"
    permission_required = ('turnos_app.es_medico')

    def get(self, request):
        if request.is_ajax():
            if(request.GET['medico_pk']):
                medico = Medico.objects.get(pk=request.GET['medico_pk'])
                turnos_confirmados = Turno.objects.filter(estado=3, medico=medico).order_by('-prioridad', 'fecha')
                data = {"turnos_confirmados": turnos_confirmados}
                return render(request, self.template_name, data)
            else:
                return render(request, self.template_name, {})
        else:
            return render(request, self.template_name, {})


@login_required(login_url='/medico/login/')
@permission_required('turnos_app.es_medico')
def atender_turno(request, pk):
    turno = Turno.objects.get(pk=pk)
    user_paciente = turno.paciente.user
    
    if request.method == 'POST':
        form = AtenderTurnoForm(request.POST)

        if form.is_valid():
            diagnostico = form.cleaned_data.get("diagnostico")
            turno.estado = 4
            turno.save()
            TurnoAtendido.objects.create(turno=turno, diagnostico=diagnostico)
            messages.info(request, 'Turno atendido con éxito!')
            return redirect('lista-turnos-confirmados')
        else:
            messages.warning(request, 'Se ha producido un error, por favor vuelva a intentarlo.')
            return super().get(request, *args, **kwargs)        
    else:
        form = AtenderTurnoForm()
        return render(request, 'medico/atender_turno.html', {'form':form, 'paciente':user_paciente, 'prioridad':turno.prioridad})

@login_required(login_url='/medico/login/')
@permission_required('turnos_app.es_medico')
def cancelar_turno_medico(request, pk):
    
    if request.method == 'POST':
        turno = Turno.objects.get(pk=pk)
        turno.estado = 5
        turno.save()
        paciente = turno.paciente
        paciente.penalizado = True
        paciente.fecha_despenalizacion = timezone.now() + timedelta(days=7)
        paciente.save()
        TurnoCancelado.objects.create(turno=turno)
        messages.info(request, "El turno ha sido cancelado exitosamente!")
        return redirect('lista-turnos-confirmados')
    else:
        return redirect('listar-turnos-confirmados')


# Funcion lambda utilizada para calcular los días de los turnos
# Primer parametro es la fecha de referencia, segundo parametro es el valor del proximo dia que buscamos
# tomando como 0 = lunes al 7 = domingo.
onDay = lambda dt, day: dt + timedelta(days=(day - dt.weekday())%7)

@login_required(login_url='/medico/login/')
@permission_required('turnos_app.es_medico')
def crear_turnos(request):

    if request.method == 'POST':
        form = TurnoForm(request.POST)
        if form.is_valid():
            dias = form.cleaned_data.get('dias_atencion')
            hora_inicio = form.cleaned_data.get('hora_inicio')
            hora_fin = form.cleaned_data.get('hora_fin')
            duracion = form.cleaned_data.get('duracion_turno')
            sobreturnos = form.cleaned_data.get('sobreturnos')
            
            medico = request.user.medico

            mes_actual = timezone.now().date().month

            # Si es la primera vez que se crea un horario laboral junto con sus turnos, el sistema crea las 7 instancias de DiaLaboral
            if not DiaLaboral.objects.all():
                for i in range(0, 7):
                    DiaLaboral.objects.create(dia=i)

            horarios_laborales_existentes = HorarioLaboral.objects.filter(medico=medico)
            # Esto corrobora que no se estén superponiendo horarios laborales ya creados
            if horarios_laborales_existentes:
                for horario in horarios_laborales_existentes:
                    for dia in dias:
                        dia_laboral = DiaLaboral.objects.get(dia=dia)
                        if dia_laboral in horario.dias.all():
                            if(hora_inicio >= horario.hora_inicio and hora_inicio < horario.hora_fin) or (hora_fin > horario.hora_inicio and hora_fin <= horario.hora_fin):
                                messages.warning(request, 'Error, se detectó una superposición de Horarios')
                                return redirect('horario-laboral')                         

            # Creamos el objeto del HorarioLaboral
            horario_laboral = HorarioLaboral.objects.get_or_create(medico=medico, hora_inicio=hora_inicio, hora_fin=hora_fin, sobreturnos=sobreturnos, intervalo=duracion)[0]

            # Creamos los turnos en cada dia, con los distintos horarios posibles.
            for dia in dias:
                dia_laboral = DiaLaboral.objects.get(dia=dia)
                if not dia_laboral in horario_laboral.dias.all():
                    horario_laboral.dias.add(dia_laboral)
                    dia_turno = onDay(timezone.now().date(), int(dia))
                    while dia_turno.month == mes_actual:
                        # con el make_aware hacemos que la fecha sea de formato UTC
                        fecha_atencion = make_aware(datetime.combine(dia_turno, horario_laboral.hora_inicio))
                        while fecha_atencion.time() <= horario_laboral.hora_fin:
                            # Estado 1 = 'disponible'
                            turno = Turno.objects.create(medico=medico, estado=1, fecha=fecha_atencion)
                            fecha_atencion = fecha_atencion + timedelta(minutes=duracion)
                        # Buscamos el mismo día, pero en la semana siguiente
                        dia_turno = onDay(dia_turno + timedelta(days=7), int(dia))
            
            messages.info(request, 'Horario Laboral creado con éxito!')
            return redirect('horario-laboral')
    else:
        form = TurnoForm()
        
    return render(request, 'medico/crear_turnos.html', {'form': form})

class ListarHorariosyDiasLaborales(PermissionRequiredMixin, ListView):

    login_url = MEDICO_LOGIN_URL
    permission_required = ('turnos_app.es_medico')
    model = HorarioLaboral
    paginate_by = 10
    template_name = 'medico/horarios_laborales.html'
    
    def get_context_data(request, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        medico = request.request.user.medico
        dias = DiaLaboral.objects.all()
        horarios_laborales = HorarioLaboral.objects.filter(medico=medico)
        context['dias'] = dias
        context['horarios_laborales'] = horarios_laborales
        return context
   
@login_required(login_url='/medico/login/')
@permission_required('turnos_app.es_medico') 
def eliminar_horario_laboral(request, pk):

    if request.method == "POST":
        mes_actual = timezone.now().date().month
        horario_laboral = HorarioLaboral.objects.get(pk=pk)
        medico_logueado = request.user.medico

        if (horario_laboral.medico != medico_logueado):
            messages.warning('El Horario Laboral que intenta borrar no corresponde al Médico logueado.')
            return redirect('horario-laboral')

        for dia_laboral in horario_laboral.dias.all():
            dia_turno = onDay(date.today().replace(day=1), int(dia_laboral.dia))
            while dia_turno.month == mes_actual:
                # con el make_aware hacemos que la fecha sea de formato UTC
                fecha_turno = make_aware(datetime.combine(dia_turno, horario_laboral.hora_inicio))
                while fecha_turno.time() <= horario_laboral.hora_fin:
                    try:
                        turnos = Turno.objects.filter(medico=medico_logueado, estado=1, fecha=fecha_turno)
                        turnos.delete()
                    except Turno.DoesNotExist:
                        print("Turno para el día %s no existe!" % (fecha_turno))
                    fecha_turno = fecha_turno + timedelta(minutes=horario_laboral.intervalo)
                dia_turno = onDay(dia_turno + timedelta(days=7), int(dia_laboral.dia))

        horario_laboral.delete()

        messages.info(request, 'Horario Laboral eliminado con éxito!')
        return redirect('horario-laboral')

