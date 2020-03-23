from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse,Http404
from django.urls import reverse_lazy
from datetime import timedelta, datetime, date
from django.views.generic import ListView
from django.views.generic.edit import CreateView, UpdateView 
from django.views import View
from django.contrib import messages
from django.http import JsonResponse
import json 
from django.utils.decorators import method_decorator

from ..models import *
from .views_usuario import *
from ..forms.user_forms import CustomUserChangeForm
from ..forms.forms_recepcionista import *
from ..forms.forms_paciente import PacienteCreationForm ,PacienteChangeForm
from ..forms.forms_turno import SeleccionarEspecialidadForm, SeleccionarTurnoForm
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import Permission
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login


def get_paciente_by_documento(documento):
    try:
        user = CustomUser.objects.get(documento=documento)
        if (user.has_perm('turnos_app.es_paciente')):
            # checkear si es paciente
            paciente = Paciente.objects.get(pk=user.id)
            return paciente
        else: 
            return None
    except CustomUser.DoesNotExist:
        return None

class LoginRecepcionistaView(View):

    template_name = 'recepcionista/login.html'
    success_url = 'index-recepcionista'
    
    # loguea al recepcionista
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
                if (user.has_perm('turnos_app.es_recepcionista')):
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


@login_required(login_url='/recepcionista/login')
@permission_required('turnos_app.es_recepcionista',)
# muestra la página de inicio una vez que se loguea el recepcionista
def index_recepcionista(request):
    pk_recepcionista = request.user.pk
    recepcionista_logueado = CustomUser.objects.get(pk=pk_recepcionista)
    #informacion_form = RecepcionistaInformationForm(instance=recepcionista_logueado)
    """ obtiene todos los turnos a partir de la hora y de 2 semanas en adelante """
    return render(request,'recepcionista/index.html',{'recepcionista':recepcionista_logueado})


class AtenderUsuarioView(PermissionRequiredMixin, View):
    permission_required = ('turnos_app.es_recepcionista',)
    template_name = 'recepcionista/atender_usuario.html'

    def get(self,request,*args,**kwargs):
        documento_form = DocumentoForm()
        context = {
            'documento_form':documento_form,
        }
        return render(request, self.template_name,context)
#
    #def post(self,request,*args,**kwargs):
#
    #lista_turnos = Turno.get_turnos_fecha(Turno.objects.filter(estado=2), date.today())
    #if lista_turnos:
    #    lista_turnos_id = [turno.id for turno in lista_turnos]
    #    # turnos están ordenados por id/pk
    #    turnos = Turno.objects.filter(id__in=lista_turnos_id)
    #else: 
    #    return render(request, 'recepcionista/gestionar_turnos.html')
#
    #if request.method == 'POST':
    #    form = SeleccionarTurnoForm(turnos=turnos, data=request.POST)
    #    print('Entro al if POST')
    #    print(form)
    #    if form.is_valid():
    #        print("El form es valido")
    #        if 'confirmar' in request.POST:
    #            print("Entro al confirmar")
    #            turno = form.cleaned_data.get('turno')
    #            turno.estado = 3 # Cambio el estado a 'Confirmado'
    #            turno.save()
    #            
    #        elif 'cancelar' in request.POST:
    #            print("Entro al cancelar")
    #            turno = form.cleaned_data.get('turno')
    #            print(turno)
    #            hora_actual = timezone.now()
#
    #            # Si cancela menos de 2 horas antes
    #            if hora_actual + timedelta(hours=2) >= turno.fecha:
    #                turno.estado = 5 # Estado cancelado
    #                turno.save()
    #                turno_cancelado = TurnoCancelado.objects.create(turno=turno, fecha_cancelado=hora_actual)
    #                turno_cancelado.save()
    #                paciente.penalizado = True
    #                paciente.fecha_despenalizacion = timezone.now() + timedelta(days=2) # Lo penalizo por 2 días nomas porque fue copado y avisó
    #                paciente.save()
    #            else:
    #                turno.estado = 1 # Estado disponible
    #                turno.paciente = None
    #                turno.save()
    #        
    #    form = SeleccionarTurnoForm(turnos=turnos)
    #    return render(request, 'recepcionista/gestionar_turnos.html', {'form':form})
#

class GestionarTurnosView(PermissionRequiredMixin, View):
    permission_required = ('turnos_app.es_recepcionista',)
    template_name = 'recepcionista/gestionar_turnos.html'

    def get(self,request,*args,**kwargs):
        paciente = get_object_or_404(Paciente,pk=kwargs['pk'])
        # se obtienen los turnos del paciente pendientes para su ateción(se omite la hora de atención)
        turnos_pendientes = paciente.get_turnos_pendientes()        
        context = {
            'paciente': paciente,
            'turnos': turnos_pendientes,
        }
        return render(request,self.template_name,context)
    
    # tal vez este método no sea necesario, ya que se hacen llamadas ajax
    def post(self,request,*args,**kwargs): 
        pass


class SignUpPacienteView(PermissionRequiredMixin, CustomUserCreateView):
    form_class = PacienteCreationForm
    # debería retornar un mensaje que diga que lo registró, y luego la posibilidad de poder seguir creando
    #success_url = reverse_lazy('login')
    template_name = 'recepcionista/registrar_paciente.html'
    # being an admin, you have all permissions required to access every url in the system
    permission_required = ('turnos_app.es_recepcionista',)

    def get(self, request, *args, **kwargs): 
        return super().get(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        form = PacienteCreationForm(request.POST)
        if(form.is_valid()):
            print('Entrando al is_valid(), previo a llamada super()')
            kwargs['user_permission_codename'] = 'es_paciente'
            super().post(request, *args, **kwargs)

            user = CustomUser.objects.get(documento=form.cleaned_data.get('documento'))
            genero = form.cleaned_data.get('genero')
            if(form.cleaned_data['obra_social'] is None):
                perfil_paciente = Paciente.objects.create(user=user, genero=genero)
            else:
                obra_social = form.cleaned_data.get('obra_social')
                obra_social.pacientes += 1
                obra_social.save()
                perfil_paciente = Paciente.objects.create(user=user, genero=genero, obra_social=obra_social)
            perfil_paciente.save()
            messages.info(request, 'Paciente creado con éxito!')
            return redirect('registrar-paciente')
        else:
            print('Error de validacion de formulario')
            messages.warning(request, 'Se ha producido un error, por favor vuelva a intentarlo.')
            return super().get(request, *args, **kwargs)

@login_required(login_url='/recepcionista/login')
@permission_required('turnos_app.es_recepcionista')
def editar_informacion_paciente(request, pk):

    user = get_object_or_404(CustomUser, pk=pk)
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, instance=user)
        paciente_form = PacienteChangeForm(request.POST, instance=user.paciente)

        if form.is_valid() and paciente_form.is_valid():
            user = form.save()
            paciente = paciente_form.save(False)
            paciente.user = user
            paciente.save()
            return redirect('home')        
    else:
        form = CustomUserChangeForm(instance=user)
        paciente_form = PacienteChangeForm(instance=user.paciente)
        args = {'form': form, 'perfil_form': paciente_form}
        return render(request, 'recepcionista/editar_paciente.html', args)

class ReservarTurnoView(PermissionRequiredMixin,View):

    template_name = 'recepcionista/reservar_turno.html'
    permission_required = ('turnos_app.es_recepcionista',)

    def get(self,request,*args,**kwargs):
        paciente = get_object_or_404(Paciente,pk=kwargs['pk'])
        especialidades = Especialidad.objects.all()
        especialidades_form = SeleccionarEspecialidadForm(especialidades=especialidades)
        context = {
            'paciente':paciente,
            'especialidad_form':especialidades_form,
        }
        return render(request,self.template_name,context)

    def post(self,request,*args,**kwargs):
        especialidades_form = SeleccionarEspecialidadForm(especialidades=Especialidad.objects.all(),data=request.POST)
        print(request.POST)
        if  ("reservar" in request.POST):
            turno_id = request.POST['turnos']
            # lógica para reservar turno
            return redirect('completar-reserva',pk=turno_id,documento=request.POST['documento'])
        elif (especialidades_form.is_valid()):
            especialidad_seleccionada = especialidades_form.cleaned_data.get('especialidades')
            # obtener primero los médicos por esp1ecialidad
            medicos_especialidad = Medico.objects.filter(especialidad=especialidad_seleccionada)
            medicos_id = [
                medico.user_id for medico in medicos_especialidad
            ]
            # luego obtener los turnos por médico, falta filtrarlos por medico
            turnos_especialidad = Turno.get_turnos_weeks_ahead(estado=1).filter(medico_id__in=medicos_id)
            return render(request,self.template_name,{'especialidad_form':especialidades_form})    

class ImprimirReservaView(PermissionRequiredMixin,View):

    template_name = 'recepcionista/imprimir_reserva.html'
    permission_required = ('turnos_app.es_recepcionista',)

    def get(self,request,*args,**kwargs):
        # mejor podría ser el método get_or_404
        turno_reservado = get_object_or_404(Turno,pk=kwargs['pk'])
        user = CustomUser.objects.get(pk=kwargs['pacientepk'])
        paciente = Paciente.objects.get(user_id=user.id)
        # el estado del turno ya estará en Estado 2 = 'Reservado'
        # luego verificar por rango de fecha
        if (turno_reservado.paciente.user.pk != user.pk) or (turno_reservado.fecha.date() < datetime.date.today()):
            raise Http404('Página no encontrada')   
        context = {
            'turno':turno_reservado,
            'paciente': paciente, 
        }
        return render(request,'recepcionista/imprimir_reserva.html',context)
    
    def post(self,request,*args,**kwargs):
        print(request.POST)
        
        turno_reservado = get_object_or_404(Turno,pk=request.POST['turno'])

# RECECEPCIONISTA AJAX VIEWS

class ObtenerPacienteAjax(PermissionRequiredMixin,View):

    template_name = 'recepcionista/tarjeta_paciente.html'
    permission_required = ('turnos_app.es_recepcionista')

    def get(self,request):
        if request.is_ajax():
            if(request.GET['documento']):
                paciente = get_paciente_by_documento(request.GET['documento'])
                if paciente is not None:
                    return render(request,self.template_name,{'paciente':paciente})
                else:
                    return render(request,self.template_name,{})
            else:
                return render(request,self.template_name,{})

class ConsultarTurnosEspecialidadAjax(PermissionRequiredMixin,View):

    permission_required = ('turnos_app.es_recepcionista',)

    def get(self,request):
        if request.is_ajax():
            especialidad = request.GET['especialidades']
            # obtener los médicos por especialidad
            medicos_especialidad = Medico.objects.filter(especialidad=especialidad)
            medicos_id = []
            # creo una lista de ids con los medicos obtenidos
            for medico in medicos_especialidad:
                medicos_id.append(medico.user_id)
            # obtengo los turnos por un rango de fecha, en este caso 2 semanas y Estado = 1: Disponible
            time_dt = timedelta(weeks=2)
            day_dt = timedelta(days=1)
            # debería filtrar por fecha en lugar de fecha y hora
            startdate = datetime.datetime.now() - day_dt
            # debería filtrar por fecha en lugar de fecha y hora
            enddate = datetime.datetime.now() + time_dt
            turnos = Turno.objects.filter(medico_id__in=medicos_id,estado=1,fecha__range=[startdate,enddate]).order_by('fecha')
            turno_form = SeleccionarTurnoForm()
            turno_form.set_turnos(turnos=turnos)
            context = {
                'turnos_form':turno_form
            }
            return render(request,'recepcionista/buscar_turnos.html',context)

class RealizarReservaAjax(PermissionRequiredMixin, View):

    permission_required = ('turnos_app.es_recepcionista',)
    view_url = 'recepcionista/imprimir-reserva/'

    def post(self, request, *args, **kwargs):
        if request.is_ajax():
            turno_seleccionado = Turno.objects.get(pk=request.POST['turnos'])
            paciente = Paciente.objects.get(user_id=request.POST['paciente'])
            # Estado 1 = 'Disponible'
            if turno_seleccionado.estado == 1:
                # Estado 2 = 'Reservado'
                turno_seleccionado.estado = 2
                turno_seleccionado.paciente = paciente
                turno_seleccionado.save()
                redirect_url  ='/' + self.view_url + str(paciente.user.pk) + '/' + str(turno_seleccionado.pk) + '/';
                response_data = {
                    'redirect_url':redirect_url,
                    'message':'Turno Reservado con éxito',
                }
                return JsonResponse(data=response_data,status=200)
            else: 
                response_data = {
                    'esta_reservado': True,
                    'message':'El turno seleccionado ya ha sido reservado',
                }
                return JsonResponse(data=response_data,status=200)

class ConfirmarReservaAjax(PermissionRequiredMixin, View):

    permission_required = ('turnos_app.es_recepcionista',)

    def put(self, request, *args, **kwargs):
        if request.is_ajax():
            received_data = json.loads(request.body)
            print(received_data)
            action = received_data['action']
            turno_pk = received_data['turno']  
            turno_a_modificar = get_object_or_404(Turno,pk=turno_pk)
            data = {}
            print('ACTION METHOD: ' + action)
            print('TURNO PK: ' + turno_pk)
            if (action == 'confirmar'):
                # Estado 3 = 'Confirmado'
                turno_a_modificar.estado = 3
                turno_a_modificar.save()
                data = {
                    'estado_turno':turno_a_modificar.get_estado_display(),
                    'confirmado':True,
                }
                return JsonResponse(data,status=200)
            elif (action == 'cancelar'):
                # Estado 5 = 'Cancelado'
                turno_a_modificar.estado = 5
                turno_a_modificar.save()
                turno_cancelado = TurnoCancelado.objects.create(turno=turno_a_modificar,fecha_cancelado=datetime.date.today())
                data = {
                    'estado_turno':turno_a_modificar.get_estado_display(),
                    'cancelado':True,
                }
                return JsonResponse(data,status=200)