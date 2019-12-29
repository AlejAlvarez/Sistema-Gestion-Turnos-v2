from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import  ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView

from datetime import timedelta, datetime, date
from app_turnos.models import Turno 
from ..models import CustomUser
from ..forms.form_recepcionista import RecepcionistaInformationForm
from ..forms.user_form import CustomUserCreationForm, CustomUserChangeForm
from .views_user import check_ownership_or_403 ,CustomUserCreateView, CustomUserUpdateView
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.decorators import login_required, permission_required

@login_required
@permission_required('app_usuarios.es_recepcionista')
# muestra la página de inicio una vez que se loguea el recepcionista
def index_recepcionista(request):
    pk_recepcionista = request.user.pk
    recepcionista_logueado = CustomUser.objects.get(pk=pk_recepcionista)
    informacion_form = RecepcionistaInformationForm(instance=recepcionista_logueado)
    """ obtiene todos los turnos a partir de la hora y de 2 semanas en adelante """
    return render(request,'usuarios/recepcionista/index.html',{'recepcionista':recepcionista_logueado,'form':informacion_form})

@login_required
@permission_required('app_usuarios.es_recepcionista')
def confirmar_turnos(request):
    pk_recepcionista = request.user.pk
    recepcionista_logueado = CustomUser.objects.get(pk=pk_recepcionista)
    """ obtiene todos los turnos del día """
    lista_turnos = Turno.get_turnos_fecha(Turno.objects.filter(estado=2), date.today())
    if lista_turnos:
        lista_turnos_id = [turno.id for turno in lista_turnos]
        turnos = Turno.objects.filter(id__in=lista_turnos_id)

    return render(request,'usuarios/recepcionista/confirmar_turnos.html',{'recepcionista':recepcionista_logueado,'turnos':lista_turnos})    

class SignUpRecepcionistaView(PermissionRequiredMixin,CustomUserCreateView):
    permission_required = ('login_required','is_staff','is_superuser')

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
        
    def post(self, request, *args, **kwargs):
        kwargs['user_permission_codename'] = 'es_recepcionista'
        return super().post(request, *args, **kwargs)

class UpdateRecepcionistaView(PermissionRequiredMixin,CustomUserUpdateView):
    permission_required = ('login_required','app_usuarios.es_recepcionista')
    
    def get(self, request, pk):
        usuario = get_object_or_404(CustomUser, pk=pk)