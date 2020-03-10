from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse,Http404
from django.urls import reverse_lazy
from django.views.generic import ListView
from django.views.generic.edit import CreateView, UpdateView 
from django.views import View

from ..models import *
from .views_usuario import *
from ..forms.user_forms import CustomUserChangeForm
from ..forms.forms_paciente import PacienteCreationForm
from ..forms.forms_recepcionista import DocumentoForm
from ..forms.forms_turno import SeleccionarEspecialidadForm
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import Permission
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login
from datetime import timedelta, datetime, date


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
@permission_required('turnos_app.es_recepcionista')
# muestra la página de inicio una vez que se loguea el recepcionista
def index_recepcionista(request):
    pk_recepcionista = request.user.pk
    recepcionista_logueado = CustomUser.objects.get(pk=pk_recepcionista)
    #informacion_form = RecepcionistaInformationForm(instance=recepcionista_logueado)
    """ obtiene todos los turnos a partir de la hora y de 2 semanas en adelante """
    return render(request,'recepcionista/index.html',{'recepcionista':recepcionista_logueado})


@login_required(login_url='/recepcionista/login')
@permission_required('turnos_app.es_recepcionista')
def gestionar_turnos(request):
    lista_turnos = Turno.get_turnos_fecha(Turno.objects.filter(estado=2), date.today())
    if lista_turnos:
        lista_turnos_id = [turno.id for turno in lista_turnos]
        # turnos están ordenados por id/pk
        turnos = Turno.objects.filter(id__in=lista_turnos_id)
    else: 
        return render(request, 'recepcionista/gestionar_turnos.html')

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
        return render(request, 'recepcionista/gestionar_turnos.html', {'form':form})
    else:
        turnostable = SeleccionarTurnoTableForm(turnos=turnos)
        form = SeleccionarTurnoForm(turnos=turnos)
        return render(request, 'recepcionista/gestionar_turnos.html', {'form':form,'turnostable':turnostable})


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
        documento_form = DocumentoForm()
        especialidades = Especialidad.objects.all()
        especialidades_form = SeleccionarEspecialidadForm(especialidades=especialidades)
        context = {
            'especialidad_form':especialidades_form,
            'documento_form': documento_form,
        }
        return render(request,self.template_name,context)

    def post(self,request,*args,**kwargs):
        especialidades_form = SeleccionarEspecialidadForm(especialidades=Especialidad.objects.all(),data=request.POST)
        print(request.POST)
        if  ("reservar" in request.POST):
            turno_id = request.POST.get('turnos')
            # lógica para reservar turno
            return redirect('completar-reserva',pk=turno_id)
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


class CompletarReservaView(PermissionRequiredMixin,View):

    template_name = 'recepcionista/completar_reserva.html'
    permission_required = ('turnos_app.es_recepcionista',)

    def get(self,request,*args,**kwargs):
        # mejor podría ser el método get_or_404
        turno_reservado = get_object_or_404(Turno,pk=kwargs['pk'])
        # primero verificar por estado, estado 1 = disponible
        # luego verificar por rango de fecha
        if turno_reservado.estado != 1:
            raise Http404('Página no encontrada')   
        context = {
            'turno':turno_reservado
        }
        return render(request,'recepcionista/completar_reserva.html',context)
    
    def post(self,request,*args,**kwargs):
        print('POST')
        """
        # POST method 
        if(form.is_valid()):
            turno = Turno.objects.get(id=form.cleaned_data.get('turno_id'))
            # estado 2 = reservado
            turno.estado = 2
            #turno.paciente = Paciente.objects.get(dni = dni)
            turno.save()
            return HttpResponse("Turno Reservado con éxito titán")
        else:
            return render(request,'recepcionista/completar_reserva.html',{'form':form}) """