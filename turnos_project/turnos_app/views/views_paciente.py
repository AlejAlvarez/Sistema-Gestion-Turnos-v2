from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import ListView
from django.views.generic.edit import CreateView, UpdateView 
from django.views import View
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.db import transaction, DatabaseError
from django.http import JsonResponse

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
                if (user.has_perm('turnos_app.es_paciente')):
                    login(request,user) 
                    next = request.session.get('next', None)
                    if next:
                        return redirect(next)    
                    return redirect(self.success_url)
                else:
                    context = {
                        'auth_form':auth_form,
                        'error_message':'No tiene permiso para acceder a esta página', 
                    }
                    return render(request,self.template_name,context)
            context = {
                'auth_form':auth_form,
                'error_message':'No tiene permiso para acceder a esta página',
            }
            return render(request,self.template_name,context)
        else:
            context = {
                'auth_form':auth_form,                
                'error_message':'Nombre de Usuario o Contraseña Incorrecto',
            }
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

    permission_required = ('turnos_app.es_paciente',) 
    template_name = 'paciente/reservar_turno.html'

    def get(self, request, *args, **kwargs): 
        especialidad_form = BuscarEspecialidadForm()
        medico_form = BuscarTurnosByMedicoForm()
        context = {
            'especialidad_form': especialidad_form,
            'medico_form':medico_form,
        }       
        return render(request, self.template_name, context) 

class ListarTurnos(PermissionRequiredMixin, ListView):
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
    permission_required = ('turnos_app.es_paciente')
    model = Turno
    template_name = 'paciente/informacion_turno.html'

class CancelarTurnoView(PermissionRequiredMixin, View):
    
    permission_required = ('turnos_app.es_paciente')
    template_name = 'paciente/cancelar_turno.html'

    def get(self, request, *args, **kwargs):
        turno = Turno.objects.get(pk=kwargs['pk'])
        paciente = Paciente.objects.get(user_id=request.user.pk)
        if turno.paciente == paciente:
            context = {
                'turno':turno,
            }
            return render(request,self.template_name,context)
        else:
            raise PermissionDenied

    def post(self,request, *args, **kwargs):
        turno = Turno.objects.get(pk=kwargs['pk'])
        hora_actual = timezone.now()
        turno.estado = 5 # Estado cancelado
        turno.save()
        turno_cancelado = TurnoCancelado.objects.create(turno=turno, fecha_cancelado=hora_actual)
        turno_cancelado.save()
        # Si cancela menos de 2 horas antes
        if hora_actual + timedelta(hours=2) >= turno.fecha:
            paciente = Paciente.objects.get(pk=request.user.pk)
            paciente.penalizado = True
            # Lo penalizo por 2 días nomas porque fue copado y avisó
            paciente.fecha_despenalizacion = timezone.now() + timedelta(days=2) 
            paciente.save()
        # Se crea un nuevo turno disponible con los datos del turno cancelado
        nuevo_turno_disponible = Turno.objects.create(estado=1,fecha=turno.fecha,medico=turno.medico)
        nuevo_turno_disponible.save()
        return redirect('turno-cancelado',pk=turno.pk)

class TurnoCanceladoView(PermissionRequiredMixin, View):
    
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

@login_required(login_url=PACIENTE_LOGIN_URL)
@permission_required('turnos_app.es_paciente')
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

    return redirect('mis-turnos')

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