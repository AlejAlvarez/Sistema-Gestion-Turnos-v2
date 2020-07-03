from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse,Http404
from django.urls import reverse_lazy
from datetime import timedelta, date
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
from ..forms.forms_turno import SeleccionarEspecialidadForm, SeleccionarTurnoForm, SeleccionarMedicoForm, CrearSobreturnoForm
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import Permission
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login


RECEPCIONISTA_PERMISSION = 'turnos_app.es_recepcionista' 
RECEPCIONISTA_LOGIN_URL = '/recepcionista/login/'

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
        if request.user.is_authenticated and request.user.has_perm(RECEPCIONISTA_PERMISSION):
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
        context = {
            'auth_form': auth_form,
        }        
        if auth_form.is_valid():
            username = auth_form.cleaned_data['username']
            password = auth_form.cleaned_data['password']
            user = authenticate(username=username,password=password)
            if user is not None:
                # se comprueba que tenga el permiso necesario para ingresar
                if (user.has_perm('turnos_app.es_recepcionista') and not(user.has_perm('turnos_app.is_staff'))):
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
            messages.error(request,'Nombre de usuario o contraseña incorrectos')
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
    login_url = RECEPCIONISTA_LOGIN_URL
    permission_required = ('turnos_app.es_recepcionista',)
    template_name = 'recepcionista/atender_usuario.html'

    def get(self,request,*args,**kwargs):
        documento_form = DocumentoForm()
        context = {
            'documento_form':documento_form,
        }
        return render(request, self.template_name,context)

class GestionarTurnosView(PermissionRequiredMixin, View):
    login_url = RECEPCIONISTA_LOGIN_URL
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
    login_url = RECEPCIONISTA_LOGIN_URL
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
            messages.success(request,"El paciente ha sido creado con éxito")
            return redirect('registrar-paciente')
        else:
            print('Error de validacion de formulario')
            return render(request,self.template_name,{'form':form})

class PacienteUpdateView(PermissionRequiredMixin, CustomUserUpdateView):
    login_url = RECEPCIONISTA_LOGIN_URL
    template_name = 'recepcionista/actualizar_paciente.html'
    # being an admin, you have all permissions required to access every url in the system
    permission_required = ('turnos_app.es_recepcionista',)

    def get(self, request, *args, **kwargs):
        user = get_object_or_404(CustomUser, pk=kwargs['pk']) 
        user_form = CustomUserChangeForm(instance=user)
        paciente_form = PacienteChangeForm(instance=user.paciente)
        context = {
            'user_form':user_form,
            'paciente_form':paciente_form,
        }
        return render(request,self.template_name,context)

    def post(self, request, *args, **kwargs):
        user = get_object_or_404(CustomUser, pk=kwargs['pk'])
        if user.has_perm('turnos_app.es_paciente'):
            user_form = CustomUserChangeForm(request.POST,instance=user)
            paciente_form = PacienteChangeForm(request.POST,instance=user.paciente)
            context = {
                'user_form':user_form,
                'paciente_form':paciente_form,
            }
            if user_form.is_valid() and paciente_form.is_valid():
                user = user_form.save()
                paciente = paciente_form.save(False)
                paciente.user = user
                paciente.save()
                messages.info(request, 'Paciente actualizado con éxito!')
                return render(request,self.template_name,context)
            else:
                return render(request,self.template_name,context)
        else:
            raise PermissionDenied

# Código que no se usa
# @login_required(login_url='/recepcionista/login')
# @permission_required('turnos_app.es_recepcionista')
# def editar_informacion_paciente(request, pk):
# 
#     user = get_object_or_404(CustomUser, pk=pk)
#     if request.method == 'POST':
#         form = CustomUserChangeForm(request.POST, instance=user)
#         paciente_form = PacienteChangeForm(request.POST, instance=user.paciente)
# 
#         if form.is_valid() and paciente_form.is_valid():
#             user = form.save()
#             paciente = paciente_form.save(False)
#             paciente.user = user
#             paciente.save()
#             return redirect('home')        
#     else:
#         form = CustomUserChangeForm(instance=user)
#         paciente_form = PacienteChangeForm(instance=user.paciente)
#         args = {'form': form, 'perfil_form': paciente_form}
#         return render(request, 'recepcionista/editar_paciente.html', args)

class ReservarTurnoView(PermissionRequiredMixin,View):

    login_url = RECEPCIONISTA_LOGIN_URL
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

    login_url = RECEPCIONISTA_LOGIN_URL
    template_name = 'recepcionista/imprimir_reserva.html'
    permission_required = ('turnos_app.es_recepcionista',)

    def get(self,request,*args,**kwargs):
        # mejor podría ser el método get_or_404
        turno_reservado = get_object_or_404(Turno,pk=kwargs['pk'])
        paciente = get_object_or_404(Paciente, user_id=kwargs['pacientepk'])
        # el estado del turno ya estará en Estado 2 = 'Reservado'
        # luego verificar por rango de fecha
        if (turno_reservado.paciente.user.pk != paciente.user.pk) or (turno_reservado.fecha.date() < date.today()):
            raise Http404('Página no encontrada')   
        context = {
            'turno':turno_reservado,
            'paciente': paciente, 
        }
        return render(request,'recepcionista/imprimir_reserva.html',context)
    
    def post(self,request,*args,**kwargs):
        print(request.POST)
        
        turno_reservado = get_object_or_404(Turno,pk=request.POST['turno'])

class ReservarSobreturnoView(PermissionRequiredMixin, View):
    login_url = RECEPCIONISTA_LOGIN_URL
    template_name = 'recepcionista/reservar_sobreturno.html'
    permission_required = ('turnos_app.es_recepcionista',)

    def get(self, request, *args, **kwargs):
        paciente = get_object_or_404(Paciente,pk=kwargs['pk'])
        especialidades = Especialidad.objects.all()
        especialidades_form = SeleccionarEspecialidadForm(especialidades=especialidades)
        context = {
            'paciente':paciente,
            'especialidad_form':especialidades_form,
        }
        return render(request,self.template_name,context)
    
    def post(self, request, *args, **kwargs):
        paciente = get_object_or_404(Paciente,user_id=request.POST['paciente'])
        medico = get_object_or_404(Medico,user_id=request.POST['medicos'])
        return redirect('confirmar-sobreturno', pacientepk=paciente.user_id, medicopk=medico.user_id)

class ConfirmarSobreturnoView(PermissionRequiredMixin, View):
    login_url = RECEPCIONISTA_LOGIN_URL
    template_name = 'recepcionista/confirmar_sobreturno.html'
    permission_required = ('turnos_app.es_recepcionista',)

    def get(self, request, *args, **kwargs):
        paciente = get_object_or_404(Paciente,user_id=kwargs['pacientepk'])
        medico = get_object_or_404(Medico,user_id=kwargs['medicopk'])
        turnos_confirmados_hoy = Turno.objects.filter(medico=medico, estado=3, fecha__date=timezone.now().date())
        if turnos_confirmados_hoy:
            ultimo_turno_confirmado = turnos_confirmados_hoy.latest('fecha')
            fecha_sobreturno = ultimo_turno_confirmado.fecha + timedelta(minutes=15)
        else:
            fecha_sobreturno = timezone.now() + timedelta(minutes=5)
        print(fecha_sobreturno)
        sobreturno_form = CrearSobreturnoForm()
        sobreturno_form.fields['fecha_sobreturno'].initial = fecha_sobreturno
        context = {
            'paciente': paciente,
            'medico': medico,
            'fecha_sobreturno': fecha_sobreturno,
            'form': sobreturno_form,
        }
        return render(request, self.template_name, context)
    
    def post(self, request, *args, **kwargs):
        sobreturno_form = CrearSobreturnoForm(request.POST)
        if sobreturno_form.is_valid():
            # 3 horas menos por diferencia horaria
            diferencia_horaria = -timedelta(hours=3)
            paciente = get_object_or_404(Paciente,user_id=kwargs['pacientepk'])
            medico = get_object_or_404(Medico,user_id=kwargs['medicopk'])
            fecha_sobreturno = sobreturno_form.cleaned_data.get('fecha_sobreturno') + diferencia_horaria
            prioridad = sobreturno_form.cleaned_data.get('prioridad')
            sobreturno = Turno.objects.create(paciente=paciente, medico=medico, fecha=fecha_sobreturno, estado=3, prioridad=prioridad, es_sobreturno=True)
            return redirect('imprimir-reserva', pacientepk=paciente.pk, pk=sobreturno.pk)
        else:
            print('sobreturno_form invalido')
            
            




# RECECEPCIONISTA AJAX VIEWS

class ObtenerPacienteAjax(PermissionRequiredMixin,View):

    template_name = 'recepcionista/tarjeta_paciente.html'
    permission_required = ('turnos_app.es_recepcionista')

    def get(self,request):
        if request.is_ajax():
            if(request.GET['documento']):
                paciente = get_paciente_by_documento(request.GET['documento'])
                if paciente is not None:
                    paciente.comprobar_penalizaciones()
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
            # obtengo los turnos por un rango de fecha, en este caso 2 semanas y Estado = 1: Disponible
            startdate = timezone.now().date()
            enddate = timezone.now().date() + timedelta(weeks=2)
            # filtro turnos por medicos de la especialidad, y las fechas
            turnos = Turno.objects.filter(medico__in=medicos_especialidad,estado=1,fecha__date__range=[startdate,enddate]).order_by('fecha')
            turnos_form = SeleccionarTurnoForm()
            turnos_form.set_turnos(turnos=turnos)
            context = {
                'turnos_form':turnos_form
            }
            return render(request,'recepcionista/buscar_turnos.html',context)

class RealizarReservaAjax(PermissionRequiredMixin, View):

    permission_required = ('turnos_app.es_recepcionista',)
    view_url = 'recepcionista/imprimir-reserva/'

    def post(self, request, *args, **kwargs):
        if request.is_ajax():
            print(request.POST)
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
            turno_pk = received_data['turno']  
            turno_a_modificar = get_object_or_404(Turno,pk=turno_pk)
            # Estado 3 = 'Confirmado'
            turno_a_modificar.estado = 3
            turno_a_modificar.save()
            data = {
                'estado_turno':turno_a_modificar.get_estado_display(),
            }
            return JsonResponse(data,status=200)

class CancelarReservaAjax(PermissionRequiredMixin, View):

    permission_required = ('turnos_app.es_recepcionista')

    def put(self, request, *args, **kwargs):
        if request.is_ajax():
            received_data = json.loads(request.body)
            turno_pk = received_data['turno']
            turno = get_object_or_404(Turno,pk=turno_pk)
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
            # Se libera el turno dado que es cancelado al menos un día antes
            else:
                turno.estado = 1 # Estado disponible
                turno.paciente = None
                turno.save()
            data = {
                'estado_turno':turno.get_estado_display(),
            }
            return JsonResponse(data,status=200)

class ConsultarSobreturnosEspecialidadAjax(PermissionRequiredMixin, View):
    permission_required = ('turnos_app.es_recepcionista')
    
    def get(self,request):
        if request.is_ajax():
            diferencia_horaria = -timedelta(hours=3)
            fecha_hoy = timezone.now() + diferencia_horaria
            # le sumo +1 al día laboral, dado que los dias se cuentan del 0 a 6, pero los Dias Laborales son del 1 al 7
            dia_laboral_hoy = DiaLaboral.objects.get(pk=fecha_hoy.weekday() + 1)
            hora_actual = fecha_hoy.time()
            especialidad = request.GET['especialidades']
            # obtener los médicos por especialidad
            medicos_especialidad = Medico.objects.filter(especialidad=especialidad)
            medicos_id_con_sobreturnos = []
            for medico in medicos_especialidad:
                horarios = HorarioLaboral.objects.filter(medico=medico)
                for horario in horarios:
                    if dia_laboral_hoy in horario.dias.all() and hora_actual >= horario.hora_inicio and hora_actual <= horario.hora_fin and horario.sobreturnos:
                        # No debería incorporar el mismo médico más de una vez en la lista, dado que no se permite solapamiento de sus Horarios Laborales
                        medicos_id_con_sobreturnos.append(medico.user_id)
            medicos_form = SeleccionarMedicoForm()
            medicos = Medico.objects.filter(user_id__in=medicos_id_con_sobreturnos)
            medicos_form.set_medicos(medicos=medicos)
            context = {
                'medicos_form': medicos_form
            }
            return render(request, 'recepcionista/buscar_medicos.html',context)