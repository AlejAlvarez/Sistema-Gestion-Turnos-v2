from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import ListView
from django.views.generic.edit import CreateView, UpdateView 

from ..models import *
from .views_usuario import *
from ..forms.user_forms import CustomUserChangeForm
from ..forms.forms_recepcionista import PacienteCreationForm
from ..forms.forms_turno import SeleccionarEspecialidadForm
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import Permission
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login
from datetime import timedelta, datetime, date



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
                obra_social_seleccionada = ObraSocial.objects.get(nombre=form.cleaned_data['obra_social'])
                perfil_paciente = Paciente.objects.create(user=user, genero=genero, obra_social=obra_social_seleccionada)
            perfil_paciente.save()
            return HttpResponse('Paciente creado con exito')
        else:
            print('Error de validacion de formulario')
            return super().get(request, *args, **kwargs)

@login_required(login_url='/recepcionista/login')
@permission_required('turnos_app.es_rececepcionista')
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
        return render(request, 'paciente/update_user_mform.html', args)

@login_required(login_url='/recepcionista/login')
@permission_required('turnos_app.es_recepcionista')
def reservar_turno(request):

    if request.method == "POST":
        especialidades_form = SeleccionarEspecialidadForm(especialidades=Especialidad.objects.all(),data=request.POST)
        if  ("reservar" in request.POST):
            turno_id = request.POST.get('turno')
            # lógica para reservar turno
            return redirect('completar-reserva',turno_id=turno_id)
        elif (especialidades_form.is_valid()):
            especialidad_seleccionada = especialidades_form.cleaned_data.get('especialidades')
            # obtener primero los médicos por esp1ecialidad
            medicos_especialidad = Medico.objects.filter(especialidad=especialidad_seleccionada)
            medicos_id = [
                medico.user_id for medico in medicos_especialidad
            ]
            # luego obtener los turnos por médico, falta filtrarlos por medico
            turnos_especialidad = Turno.get_turnos_weeks_ahead(estado=1).filter(medico_id__in=medicos_id)
            return render(request,"recepcionista/reservar_turno.html",{'especialidad_form':especialidades_form})    
            
    else:
        user = request.user
        permissions = Permission.objects.filter(user=user)
        print("PERMISOS USUARIOS: ",permissions[0].codename)
        especialidades = Especialidad.objects.all()
        especialidades_form = SeleccionarEspecialidadForm(especialidades=especialidades)
        return render(request,'recepcionista/reservar_turno.html',{'especialidad_form':especialidades_form})

@login_required(login_url='/recepcionista/login')
@permission_required('turnos_app.es_recepcionista')
def completar_reserva(request,turno_id):
        turno_reservado = Turno.objects.get(id=turno_id)
        turno_reserva_form = CompletarReservaForm(turno=turno_reservado)
        if request.method == "GET":
            return render(request,'recepcionista/completar_reserva.html',{'form':turno_reserva_form})
        else:
            #<input type="text" name="fecha" value="2020-01-11 20:39:06" required="" id="id_fecha">
            # POST method 
            form = CompletarReservaForm(data=request.POST)
            if(form.is_valid()):
                turno = Turno.objects.get(id=form.cleaned_data.get('turno_id'))
                # estado 2 = reservado
                turno.estado = 2
                #turno.paciente = Paciente.objects.get(dni = dni)
                turno.save()
                return HttpResponse("Turno Reservado con éxito titán")
            else:
                return render(request,'recepcionista/completar_reserva.html',{'form':form})