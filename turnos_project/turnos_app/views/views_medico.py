from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.urls import reverse_lazy
from django.views.generic import ListView
from django.views.generic.edit import CreateView, UpdateView 
from django.views import View
from django.core import serializers
from django.contrib import messages

from ..models import *
from .views_usuario import *
from ..forms.user_forms import CustomUserChangeForm
from ..forms.forms_turno import SeleccionarEspecialidadForm, AtenderTurnoForm
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import Permission
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login
from datetime import timedelta, datetime, date

from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response


class LoginMedicoView(View):

    template_name = 'medico/login.html'
    success_url = 'index-medico'
    
    # loguea al medico
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
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
                if (user.has_perm('turnos_app.es_medico')):
                    login(request,user)    
                    return redirect(self.success_url)
                else:
                    context['error_message'] = 'No tiene permiso para acceder'
                    return render(request,self.template_name,context)
            context['error_message'] = 'No tiene permiso para acceder'
            return render(request,self.template_name,context)
        else:
            context['error_message'] = 'Nombre de Usuario o Contraseña Incorrecto'
            return render(request,self.template_name,context)
            
@login_required(login_url='/medico/login')
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
    permission_required = ('turnos_app.es_medico')
    model = Turno
    paginate_by = 10
#    context_object_name = 'turnos_confirmados'
    template_name = 'medico/turnos_confirmados.html'

#    def get_queryset(self):
#        self.medico = get_object_or_404(Medico, pk=self.request.user.pk)
#        turnos_confirmados = Turno.objects.filter(estado=3, medico=self.medico)
#        return turnos_confirmados
    
    def get_context_data(request, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        medico = request.request.user.medico
        turnos_confirmados = Turno.objects.filter(estado=3, medico=medico)
        context['turnos_confirmados'] = turnos_confirmados
        context['medico'] = medico
        return context

@login_required(login_url='/medico/login')
@permission_required('turnos_app.es_medico')
def get_more_turnos_confirmados(request, pk):
    medico = Medico.objects.get(pk=pk)
    turnos_confirmados = Turno.objects.filter(estado=3, medico=medico)
    data = {"turnos_confirmados": turnos_confirmados}
    return JsonResponse(data)

@login_required(login_url='/medico/login')
@permission_required('turnos_app.es_medico')
def atender_turno(request, pk):
    turno = Turno.objects.get(pk=pk)
    user_paciente = turno.paciente.user
    
    if request.method == 'POST':
        form = AtenderTurnoForm(request.POST)

        if form.is_valid():
            diagnostico = form.cleaned_data.get("diagnostico")
            turno_atendido = TurnoAtendido.objects.create(turno=turno, diagnostico=diagnostico)
            turno_atendido.save()
            turno.estado = 4
            turno.save()
            messages.info(request, 'Turno atendido con éxito!')
            return redirect('lista-turnos-confirmados')
        else:
            messages.warning(request, 'Se ha producido un error, por favor vuelva a intentarlo.')
            return super().get(request, *args, **kwargs)        
    else:
        form = AtenderTurnoForm()
        return render(request, 'medico/atender_turno.html', {'form':form, 'paciente':user_paciente})


@login_required(login_url='/medico/login')
@permission_required('turnos_app.es_medico')
def cancelar_turno_medico(request, pk):
    
    if request.method == 'POST':
        turno = Turno.objects.get(pk=pk)
        turno.estado=5
        turno.save()
        turno_cancelado = TurnoCancelado.objects.create(turno=turno)
        turno_cancelado.save()
        messages.info(request, "El turno ha sido cancelado exitosamente!")
        return redirect('lista-turnos-confirmados')
    else:
        return redirect('listar-turnos-confirmados')