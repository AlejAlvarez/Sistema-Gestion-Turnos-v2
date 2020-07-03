from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import ListView
from django.views.generic.edit import CreateView, UpdateView 
from django.views import View
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.http import Http404
from django.db import transaction, DatabaseError
from django.http import JsonResponse
from django.utils import timezone

from ..models import *
from ..forms.forms_paciente import PacienteChangeForm
from ..forms.forms_turno import BuscarEspecialidadForm, BuscarTurnosByMedicoForm
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import Permission
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic import ListView, DetailView


PACIENTE_PERMISSION = 'turnos_app.es_paciente' 
PACIENTE_LOGIN_URL = '/paciente/login/'

class LoginPacienteView(View):
    
    template_name = 'paciente/login.html'
    success_url = 'index-paciente'
    
    # loguea al paciente
    def get(self, request, *args, **kwargs):
        # el error estaría en si contiene o no el permiso
        if request.user.is_authenticated and request.user.has_perm(PACIENTE_PERMISSION):
            return redirect(self.success_url)
        else:
            next = request.GET.get('next', None)
            if next:
                request.session['next'] = next
            auth_form = AuthenticationForm()
            context = {
                'auth_form':auth_form,
            }
            return render(request,self.template_name,context)

    def post(self, request, *args, **kwargs):
        # get auth form and validate
        auth_form = AuthenticationForm(data=request.POST)
        if auth_form.is_valid():
            username = auth_form.cleaned_data['username']
            password = auth_form.cleaned_data['password']
            user = authenticate(username=username,password=password)
            if user is not None:
                # se comprueba que tenga el permiso necesario para ingresar
                if (user.has_perm('turnos_app.es_paciente') and not(user.has_perm('turnos_app.is_staff'))):
                    login(request,user)
                    user.paciente.comprobar_penalizaciones() # comprobamos si el paciente tiene o tendrá penalizaciones
                    next = request.session.get('next', None)
                    if next:
                        return redirect(next)
                    return redirect(self.success_url)
                else:
                    context = {
                        'auth_form':auth_form,
                    }
                    messages.info(request,'No tiene permiso para acceder a esta página')
                    return render(request,self.template_name,context)
            context = {
                'auth_form':auth_form,
            }
            messages.info(request,'No tiene permiso para acceder a esta página')
            return render(request,self.template_name,context)
        else:
            context = {
                'auth_form':auth_form,                
            }
            messages.error(request,'Nombre de usuario o contraseña incorrecto')
            return render(request,self.template_name,context)

# va a retornar el user que está logueado, aún así debe ser un paciente
@login_required(login_url=PACIENTE_LOGIN_URL)
@permission_required('turnos_app.es_paciente')
def index_paciente(request):
    if request.method == 'GET':
        user_pk = request.user.pk
        logged_user = get_object_or_404(CustomUser,pk=user_pk) 
        lista_turnos = Turno.historial(Paciente.objects.get(user=logged_user))
        args = {'logged_user': logged_user, 'lista_turnos':lista_turnos}
        return render(request, 'paciente/index.html', args)


@login_required(login_url=PACIENTE_LOGIN_URL)
@permission_required('turnos_app.es_paciente')
def reservar_turno_paciente(request,pk):

    if request.method == 'GET':
        turno_id = pk
        context = {
            'turno_id':turno_id
        }
        return render(request, 'paciente/confirmar_reserva_paciente.html',context)
        
    if request.method == 'POST':
        # se recibe el id del turno
        turno_id = request.POST['turno']
        turno = Turno.objects.get(pk=turno_id)
        # Estado 2 = Reservado
        turno.estado = 2
        turno.paciente = request.user.paciente
        turno.save()
        return render(request,'paciente/turno_reservado_aviso.html')
            
class BuscarTurnosView(PermissionRequiredMixin, View):
    login_url = PACIENTE_LOGIN_URL
    permission_required = ('turnos_app.es_paciente',) 
    template_name = 'paciente/reservar_turno.html'

    def get(self, request, *args, **kwargs):
        paciente = Paciente.objects.get(user_id=request.user.pk)
        if paciente.penalizado:
            context = {
                'paciente_penalizado': True,
            }
        else:
            especialidad_form = BuscarEspecialidadForm()
            medico_form = BuscarTurnosByMedicoForm()
            context = {
                'paciente_penalizado': False,
                'especialidad_form': especialidad_form,
                'medico_form':medico_form,
            }       
        return render(request, self.template_name, context) 

class ListarTurnos(PermissionRequiredMixin, ListView):
    login_url = PACIENTE_LOGIN_URL
    permission_required = ('turnos_app.es_paciente')
    model = Turno
    paginate_by = 5
    template_name = 'paciente/turnos_pendientes.html'
    context_object_name = 'lista_turnos'

    def get_queryset(self):
        """ Filtra por el usuario provisto en el request.user """
        queryset = super(ListarTurnos, self).get_queryset()
        paciente = Paciente.objects.get(pk=self.request.user.pk)
        # se filtran los turnos reservados por el usuario pendientes de atención
        lista_turnos = paciente.get_turnos_pendientes()
        return lista_turnos


class VerTurno(PermissionRequiredMixin, DetailView):
    login_url = PACIENTE_LOGIN_URL
    permission_required = ('turnos_app.es_paciente')
    model = Turno
    template_name = 'paciente/informacion_turno.html'

class CancelarTurnoView(PermissionRequiredMixin, View):
    login_url = PACIENTE_LOGIN_URL
    permission_required = ('turnos_app.es_paciente')
    template_name = 'paciente/cancelar_turno.html'

    def get(self, request, *args, **kwargs):
        turno = Turno.objects.get(pk=kwargs['pk'])
        paciente = Paciente.objects.get(user_id=request.user.pk)
        if turno.paciente == paciente:
            if turno.estado != 5: # estado cancelado
                context = {
                    'turno':turno,
                }
                return render(request,self.template_name,context)
            else: 
                return render(request,self.template_name,{})
        else:
            raise PermissionDenied

    def post(self,request, *args, **kwargs):
        turno = Turno.objects.get(pk=kwargs['pk'])
        fecha_actual = timezone.now()
        # Si cancela en el mismo día, o días después
        if fecha_actual.date() >= turno.fecha.date():
            paciente = Paciente.objects.get(pk=request.user.pk)
            if (fecha_actual < turno.fecha) and (fecha_actual + timedelta(hours=2) < turno.fecha):
                # Si cancela en el mismo día, pero con mas de 2 horas de antelación, no lo penalizo
                turno.estado = 1 # Estado disponible
                turno.paciente = None
                turno.save()
            elif (fecha_actual < turno.fecha) and (fecha_actual + timedelta(hours=2) >= turno.fecha):
                # Si cancela en el mismo día, pero con menos de 2 horas de antelación, lo penalizo por 2 días nomas
                paciente.penalizado = True
                paciente.fecha_despenalizacion = datetime.now() + timedelta(days=2) 
                paciente.save()
                turno.estado = 1 # Estado disponible
                turno.paciente = None
                turno.save()
            else:
                # Si cancela en el mismo día, pero después del turno, o días después, se lo penaliza por tiempo completo de 7 días
                # A partir de la fecha del turno
                paciente.penalizado = True
                paciente.fecha_despenalizacion = turno.fecha() + timedelta(days=7) 
                paciente.save()
                turno.estado = 5 # Estado cancelado
                turno.save()
                TurnoCancelado.objects.create(turno=turno)
        else:
            # Se libera el turno dado que es cancelado al menos un día antes
            turno.estado = 1 # Estado disponible
            turno.paciente = None
            turno.save()
        return redirect('turno-cancelado',pk=turno.pk)

class TurnoCanceladoView(PermissionRequiredMixin, View):
    login_url = PACIENTE_LOGIN_URL
    permission_required = ('turnos_app.es_paciente')
    template_name = 'paciente/turno_cancelado.html'

    def get(self, request, *args ,**kwargs):
        turno_cancelado = Turno.objects.get(pk=kwargs['pk'])
        if turno_cancelado.estado == 1  or turno_cancelado.estado == 5:
            context = {
                'turno':turno_cancelado,
            }
            return render(request,self.template_name,context)
        else:
            raise Http404()

# Codigo 'duplicado'. Para esta funcionalidad referirse a 'CancelarTurnoView'
# @login_required(login_url=PACIENTE_LOGIN_URL)
# @permission_required('turnos_app.es_paciente')
# def cancelar_turno(request, pk):
#     
#     turno = Turno.objects.get(pk=pk)
#     hora_actual = datetime.now()
# 
#     # Si cancela menos de 2 horas antes
#     if hora_actual + timedelta(hours=2) >= turno.fecha:
#         turno.estado = 5 # Estado cancelado
#         turno.save()
#         turno_cancelado = TurnoCancelado.objects.create(turno=turno, fecha_cancelado=hora_actual)
#         turno_cancelado.save()
#         paciente.penalizado = True
#         paciente.fecha_despenalizacion = datetime.now() + timedelta(days=2) # Lo penalizo por 2 días nomas porque fue copado y avisó
#         paciente.save()
#     else:
#         turno.estado = 1 # Estado disponible
#         turno.paciente = None
#         turno.save()
# 
#     return redirect('mis-turnos')

class HistorialPacienteView(PermissionRequiredMixin, ListView):

    permission_required = ('turnos_app.es_paciente',)
    model = Turno
    paginate_by = 10
    context_object_name = 'lista_turnos'
    template_name = 'paciente/historial_paciente.html'

    def get_queryset(self):
        self.paciente = get_object_or_404(Paciente,pk=self.request.user.pk)
        return Turno.historial(paciente=self.paciente)

class ReservarTurnoAjax(PermissionRequiredMixin, View):

    permission_required = ('turnos_app.es_paciente',)

    def post(self, request, *args, **kwargs):
        if request.is_ajax():    
            # turno_ocupado retornará True si ya fue ocupado por otro paciente antes de consultar la reserva
            response_data = {
                'turno_ocupado':None,
            }
            paciente = Paciente.objects.get(pk=request.user.pk)
            turno_seleccionado = Turno.objects.select_for_update(nowait=True).get(pk=request.POST['turnos'])
            try:
                with transaction.atomic():
                    if turno_seleccionado.is_disponible():
                        turno_seleccionado.reservar(paciente=paciente)
                        turno_seleccionado.save()
                        response_data['turno_ocupado'] = False
                        return JsonResponse(data=response_data)
                    else:
                        response_data['turno_ocupado'] = True
                        return JsonResponse(data=response_data)
            # DatabaseError will be thrown because the turno object call is non-blocking
            except DatabaseError:
                response_data['turno_ocupado'] = True
                return JsonResponse(data=response_data)