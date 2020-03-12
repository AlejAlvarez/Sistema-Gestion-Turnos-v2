from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import ListView
from django.views.generic.edit import CreateView, UpdateView 
from django.views import View

from ..models import *
from ..forms.forms_paciente import PacienteChangeForm
from ..forms.forms_turno import BuscarEspecialidadForm, BuscarTurnosByMedicoForm
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import Permission
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic import ListView, DetailView


class LoginPacienteView(View):
    
    template_name = 'paciente/login.html'
    success_url = 'index-paciente'
    
    # loguea al paciente
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
        if auth_form.is_valid():
            username = auth_form.cleaned_data['username']
            password = auth_form.cleaned_data['password']
            user = authenticate(username=username,password=password)
            if user is not None:
                # se comprueba que tenga el permiso necesario para ingresar
                if (user.has_perm('turnos_app.es_paciente')):
                    login(request,user)    
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
@login_required(login_url='/paciente/login')
@permission_required('turnos_app.es_paciente')
def index_paciente(request):
    user_pk = request.user.pk
    logged_user = get_object_or_404(CustomUser,pk=user_pk) 
    lista_turnos = Turno.historial(Paciente.objects.get(user=logged_user))
    args = {'logged_user': logged_user, 'lista_turnos':lista_turnos}
    return render(request, 'paciente/index.html', args)


@login_required(login_url='/paciente/login')
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
            
            

class ListarTurnos(PermissionRequiredMixin, ListView):
    permission_required = ('turnos_app.es_paciente')
    model = Turno
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

@login_required(login_url='/paciente/login')
@permission_required('turnos_app.es_paciente')
def buscar_turnos(request):

    if (request.method == 'POST'):
        turno_id = request.POST['turnos']
        return redirect ('confirmar-reserva',pk=turno_id)

    """  if request.method == "POST":
        form = BuscarTurnosForm(request.POST)
        if form.is_valid():
            especialidad = form.cleaned_data.get('especialidad')
            medico = form.cleaned_data.get('medico')
            fecha = form.cleaned_data.get('fecha')
            lista_turnos = []
            if medico == None:
                lista_medicos = Medico.objects.filter(especialidad=especialidad)
                for medico in lista_medicos:
                    # Estado 1 = 'Disponible'
                    lista_turnos_medico = Turno.objects.filter(medico=medico, estado=1)
                    # Voy concatenando las listas de turnos
                    lista_turnos.extend(Turno.get_turnos_fecha(lista_turnos_medico, fecha))
                lista_turnos.sort(key=lambda turno: turno.fecha)
            else:
                # Estado 1 = 'Disponible'
                lista_turnos_medico = Turno.objects.filter(medico=medico, estado=1)
                # Consigo los turnos de una determinada fecha
                lista_turnos = Turno.get_turnos_fecha(lista_turnos_medico, fecha)
                lista_turnos.sort(key=lambda turno: turno.fecha)

            if lista_turnos:
                # Parece que esto se podría hacer con Django Cache Framework
                request.session['lista_turnos'] = serializers.serialize('json', lista_turnos)
                return redirect('reservar-turno')
            else:
                return HttpResponse("Lo sentimos, no se han encontrado turnos disponibles en la fecha seleccionada.")
    """
    if request.method == "GET":
        especialidad_form = BuscarEspecialidadForm()
        medico_form = BuscarTurnosByMedicoForm()
        return render(request, 'paciente/accion_turno.html', {'especialidad_form': especialidad_form,'medico_form':medico_form, 'accion': "Buscar"})

# Es necesario este metodo???
@login_required(login_url='/paciente/login')
@permission_required('turnos_app.es_paciente')
def reservar_turno(request):

    if not request.session['lista_turnos']:
        return HttpResponse('Debe realizar una búsqueda de turnos primero.')
    lista_turnos_id = []
    for turno in serializers.deserialize('json', request.session['lista_turnos']):
        lista_turnos_id.append(turno.object.id)
    turnos = Turno.objects.filter(id__in=lista_turnos_id)

    if request.method == "POST":
        # Aca obtengo la fila que seleccionó el paciente (o sea, el turno), y verifico que siga disponible
        # luego, se lo reservo a este paciente
        form = SeleccionarTurnoForm(turnos=turnos, data=request.POST)
        if form.is_valid():
            usuario = CustomUser.objects.get(pk=request.user.pk)
            paciente = Paciente.objects.get(user=usuario)
            if paciente.penalizado:
                if paciente.fecha_despenalizacion > datetime.date.today():
                    # Lo reboto porque todavía está penalizado
                    return HttpResponse('Usted actualmente se encuentra penalizado. \n Podrá solicitar turnos a partir del día %s' % (paciente.fecha_despenalizacion))
                else:
                    # Cumplió su condena. Lo despenalizo
                    paciente.despenalizar()
                    paciente.save()
            turno = form.cleaned_data.get('turno')
            if turno.estado == 1:
                turno.paciente = paciente
                # Cambio el estado del turno a 'Reservado'
                turno.estado = 2 
                turno.save()
            else:
                return HttpResponse("Lo sentimos, ese turno parece ya no estar disponible. \n Por favor, seleccione otro.")

            return HttpResponse("Su turno, Sr/Sra %s ha sido reservado con éxito! La fecha será %s" % (request.user, turno.fecha))
    else: 
        # Renderizo la datatable con los datos de los turnos        
        form = SeleccionarTurnoForm(turnos=turnos)
        return render(request, 'paciente/accion_turno.html', {'form':form, 'accion': "Reservar"})

@login_required(login_url='/paciente/login')
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


@login_required(login_url='/paciente/login')
@permission_required('turnos_app.es_paciente')
def ver_historial(request):

    paciente = Paciente.objects.get(pk=request.user.pk)
    turnos = Turno.historial(paciente=paciente)

    return render(request, 'paciente/historial_paciente.html', {'lista_turnos':turnos})