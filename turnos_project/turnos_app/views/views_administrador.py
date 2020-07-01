from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, TemplateView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views import View
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin

from ..models import *
from .views_usuario import *
from ..forms.user_forms import CustomUserChangeForm
from ..forms.forms_medico import MedicoCreationForm, MedicoChangeForm
from ..forms.forms_paciente import PacienteCreationForm
from ..forms.forms_turno import SeleccionarEspecialidadForm
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import Permission
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login
from datetime import timedelta, date

from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response


ADMINISTRADOR_PERMISSION = 'turnos_app.es_administrador'
ADMINISTRADOR_LOGIN_URL = '/administrador/login/'

class LoginAdministradorView(View):

    template_name = 'administrador/login.html'
    success_url = 'index-administrador'
    
    # loguea al administrador
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.has_perm(ADMINISTRADOR_PERMISSION):
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
                if (user.has_perm('turnos_app.es_administrador') and not(user.has_perm('turnos_app.is_staff'))):
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


@login_required(login_url='/administrador/login')
@permission_required('turnos_app.es_administrador')
# muestra la página de inicio una vez que se loguea el administrador
def index_administrador(request):
    pk_administrador = request.user.pk
    administrador_logueado = CustomUser.objects.get(pk=pk_administrador)
    '''
    usuarios = CustomUser.objects.all()
    lista_recepcionistas = []
    lista_medicos = []
    lista_administradores = []
    for usuario in usuarios:
        if usuario.has_perm('turnos_app.es_recepcionista') and not usuario.has_perm('turnos_app.es_administrador'): # Esta consulta es debido a que el admin es considerado recepcionista tambien
            lista_recepcionistas.append(usuario)
        elif usuario.has_perm('turnos_app.es_medico') and not usuario.has_perm('turnos_app.es_administrador'):
            lista_medicos.append(usuario)
        elif usuario.has_perm('turnos_app.es_administrador') and not usuario.has_perm('turnos_app.es_recepcionista'):
            lista_administradores.append(usuario)
    #informacion_form = AdministradorInformationForm(instance=administrador_logueado)
    """ obtiene todos los turnos a partir de la hora y de 2 semanas en adelante """
    print(lista_recepcionistas)
    return render(request,'administrador/index.html',{'administrador_logueado':administrador_logueado, 'lista_recepcionistas':lista_recepcionistas,
                                                        'lista_medicos':lista_medicos, 'lista_administradores':lista_administradores,})
    '''
    return render(request, 'administrador/index.html', {'administrador':administrador_logueado})


class SignUpRecepcionistaView(PermissionRequiredMixin, CustomUserCreateView):

    login_url = ADMINISTRADOR_LOGIN_URL
    form_class = CustomUserCreationForm
    template_name = 'administrador/registrar_recepcionista.html'
    permission_required = ('turnos_app.es_administrador')
    
    def get(self, request, *args, **kwargs): 
        return super().get(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        form = CustomUserCreationForm(request.POST)
        if(form.is_valid()):
            print('Entrando al is_valid(), previo a llamada super()')
            kwargs['user_permission_codename'] = 'es_recepcionista'
            super().post(request, *args, **kwargs)

            messages.info(request, 'Recepcionista creado con éxito!')
            return redirect('registrar-recepcionista')
        else:
            print('Error de validacion de formulario')
            messages.warning(request, 'Se ha producido un error, por favor vuelva a intentarlo.')
            return super().get(request, *args, **kwargs)
            

@login_required(login_url='/administrador/login')
@permission_required('turnos_app.es_administrador')
def editar_informacion_recepcionista(request, pk):

    user = get_object_or_404(CustomUser, pk=pk)
    if user.has_perm('turnos_app.es_recepcionista') and not user.has_perm('turnos_app.es_administrador'):
        if request.method == 'POST':
            form = CustomUserChangeForm(request.POST, instance=user)

            if form.is_valid():
                user = form.save()
                messages.info(request, 'Recepcionista editado con éxito!')
                return redirect('menu-recepcionistas')

            else:
                messages.warning(request, 'Se ha producido un error, por favor vuelva a intentarlo.')
                return super().get(request, *args, **kwargs)        
        else:
            form = CustomUserChangeForm(instance=user)
            return render(request, 'administrador/editar_recepcionista.html', {'form':form, 'user':user})
    else:
        print('El usuario buscado no corresponde a un recepcionista.')
        return redirect('index-administrador')
        

class DetailsRecepcionista(PermissionRequiredMixin, DetailView):

    login_url = ADMINISTRADOR_LOGIN_URL
    model = CustomUser
    template_name = 'administrador/detalles_recepcionista.html'
    permission_required = ('turnos_app.es_administrador')

class RecepcionistaListView(PermissionRequiredMixin, ListView):

    login_url = ADMINISTRADOR_LOGIN_URL
    model = CustomUser
    template_name = 'administrador/lista_recepcionistas.html'
    permission_required = ('turnos_app.es_administrador')
    
    def get_context_data(request, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        lista_recepcionistas = []
        for user in CustomUser.objects.all():
            if user.has_perm('turnos_app.es_recepcionista') and not user.has_perm('turnos_app.es_administrador'): # Esta consulta es debido a que el admin es considerado recepcionista tambien
                lista_recepcionistas.append(user)
        context['lista_recepcionistas'] = lista_recepcionistas
        return context

class EliminarRecepcionistaView(PermissionRequiredMixin, SuccessMessageMixin, DeleteView):

    login_url = ADMINISTRADOR_LOGIN_URL
    model = CustomUser
    permission_required = ('turnos_app.es_administrador')
    template_name = 'administrador/eliminar_usuario.html'
    success_url = reverse_lazy('menu-recepcionistas')
    success_message = "Recepcionista eliminado con éxito."

class SignUpMedicoView(PermissionRequiredMixin, CustomUserCreateView):
    
    login_url = ADMINISTRADOR_LOGIN_URL
    form_class = MedicoCreationForm
    template_name = 'administrador/registrar_medico.html'
    permission_required = ('turnos_app.es_administrador')
    
    def get(self, request, *args, **kwargs): 
        return super().get(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        form = MedicoCreationForm(request.POST)
        if(form.is_valid()):
            print('Entrando al is_valid(), previo a llamada super()')
            kwargs['user_permission_codename'] = 'es_medico'
            super().post(request, *args, **kwargs)

            user = CustomUser.objects.get(documento=form.cleaned_data.get('documento'))
            especialidad = form.cleaned_data.get('especialidad')
            especialidad.medicos += 1
            especialidad.save()
            cuil = form.cleaned_data.get('cuil')
            perfil_medico = Medico.objects.create(user=user, especialidad=especialidad, cuil=cuil)
            perfil_medico.save()
            messages.info(request, 'Medico creado con éxito!')
            return redirect('registrar-medico')
        else:
            print('Error de validacion de formulario')
            messages.warning(request, 'Se ha producido un error, por favor vuelva a intentarlo.')
            return super().get(request, *args, **kwargs)
            
@login_required(login_url='/administrador/login')
@permission_required('turnos_app.es_administrador')
def editar_informacion_medico(request, pk):

    user = get_object_or_404(CustomUser, pk=pk)
    if user.has_perm('turnos_app.es_medico') and not user.has_perm('turnos_app.es_administrador'):
        if request.method == 'POST':
            form = CustomUserChangeForm(request.POST, instance=user)
            medico_form = MedicoChangeForm(request.POST, instance=user.medico)

            if form.is_valid() and medico_form.is_valid():
                user = form.save()
                medico = medico_form.save(False)
                medico.user = user
                medico.save()
                messages.info(request, 'Medico editado con éxito!')
                return redirect('menu-medicos')

            else:
                messages.warning(request, 'Se ha producido un error, por favor vuelva a intentarlo.')
                return super().get(request, *args, **kwargs)
        else:
            form = CustomUserChangeForm(instance=user)
            medico_form = MedicoChangeForm(instance=user.medico)
            args = {'form': form, 'perfil_form': medico_form}
            return render(request, 'administrador/editar_medico.html', args)
    else:
        print('El usuario buscado no corresponde a un medico.')
        return redirect('index-administrador')
        
class DetailsMedico(PermissionRequiredMixin, DetailView):
    
    login_url = ADMINISTRADOR_LOGIN_URL
    model = CustomUser
    template_name = 'administrador/detalles_medico.html'
    permission_required = ('turnos_app.es_administrador')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        perfil_medico = Medico.objects.get(user=CustomUser.objects.get(documento=context['object'].documento))
        context['cuil'] = perfil_medico.cuil
        context['especialidad'] = perfil_medico.especialidad
        return context
        
class MedicoListView(PermissionRequiredMixin, ListView):
    
    login_url = ADMINISTRADOR_LOGIN_URL
    model = CustomUser
    template_name = 'administrador/lista_medicos.html'
    permission_required = ('turnos_app.es_administrador')
    
    def get_context_data(request, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        lista_medicos = []
        for user in CustomUser.objects.all():
            if user.has_perm('turnos_app.es_medico') and not user.has_perm('turnos_app.es_administrador'): # Esta consulta es debido a que el admin es considerado recepcionista tambien
                lista_medicos.append(user)
        context['lista_medicos'] = lista_medicos
        return context
    
class EliminarMedicoView(PermissionRequiredMixin, SuccessMessageMixin, DeleteView):
    
    login_url = ADMINISTRADOR_LOGIN_URL
    model = CustomUser
    permission_required = ('turnos_app.es_administrador')
    template_name = 'administrador/eliminar_usuario.html'

    def delete(self, request, *args, **kwargs):
        user = self.get_object()
        perfil = Medico.objects.get(user=user)
        especialidad = perfil.especialidad
        especialidad.medicos -= 1
        especialidad.save()
        user.delete()
        messages.info(request, 'Medico eliminado con éxito!')
        return redirect('menu-medicos')
            
class SignUpAdministradorView(PermissionRequiredMixin, CustomUserCreateView):
    
    login_url = ADMINISTRADOR_LOGIN_URL
    form_class = CustomUserCreationForm
    template_name = 'administrador/registrar_administrador.html'
    permission_required = ('turnos_app.es_administrador')
    
    def get(self, request, *args, **kwargs): 
        return super().get(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        form = CustomUserCreationForm(request.POST)
        if(form.is_valid()):
            print('Entrando al is_valid(), previo a llamada super()')
            kwargs['user_permission_codename'] = 'es_administrador'
            super().post(request, *args, **kwargs)
            messages.info(request, 'Administrador creado con éxito!')
            return redirect('registrar-administrador')
        else:
            print('Error de validacion de formulario')
            messages.warning(request, 'Se ha producido un error, por favor vuelva a intentarlo.')
            return super().get(request, *args, **kwargs)
            
@login_required(login_url='/administrador/login')
@permission_required('turnos_app.es_administrador')
def editar_informacion_administrador(request, pk):

    user = get_object_or_404(CustomUser, pk=pk)
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, instance=user)

        if form.is_valid():
            user = form.save()
            messages.info(request, 'Administrador editado con éxito!')
            return redirect('menu-administradores')

        else:
            messages.warning(request, 'Se ha producido un error, por favor vuelva a intentarlo.')
            return super().get(request, *args, **kwargs)    
    else:
        form = CustomUserChangeForm(instance=user)
        return render(request, 'administrador/editar_administrador.html', {'form':form})

class DetailsAdministrador(PermissionRequiredMixin, DetailView):
    
    login_url = ADMINISTRADOR_LOGIN_URL
    model = CustomUser
    template_name = 'administrador/detalles_administrador.html'
    permission_required = ('turnos_app.es_administrador')
    
class AdministradorListView(PermissionRequiredMixin, ListView):
    
    login_url = ADMINISTRADOR_LOGIN_URL
    model = CustomUser
    template_name = 'administrador/lista_administradores.html'
    permission_required = ('turnos_app.es_administrador')
    
    def get_context_data(request, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        lista_administradores = []
        for user in CustomUser.objects.all():
            if user.has_perm('turnos_app.es_administrador') and not user.has_perm('turnos_app.es_recepcionista'): # Esta consulta es debido a que el admin es considerado recepcionista tambien
                lista_administradores.append(user)
        context['lista_administradores'] = lista_administradores
        return context
        
class EliminarAdministradorView(PermissionRequiredMixin, SuccessMessageMixin, DeleteView):
    
    login_url = ADMINISTRADOR_LOGIN_URL
    model = CustomUser
    permission_required = ('turnos_app.es_administrador')
    template_name = 'administrador/eliminar_usuario.html'

    def delete(self, request, *args, **kwargs):
        user = self.get_object()
        if request.user.username == user.username:
            messages.warning(request, 'No puede eliminarse a usted mismo.')
            return redirect('menu-administradores')
        else:
            user.delete()
            messages.info(request, 'Administrador eliminado con éxito!')
            return redirect('menu-administradores')

class PacienteListView(PermissionRequiredMixin, ListView):
    
    login_url = ADMINISTRADOR_LOGIN_URL
    model = CustomUser
    permission_required = ('turnos_app.es_administrador')
    template_name = 'administrador/lista_pacientes.html'
    
    def get_context_data(request, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        lista_pacientes = []
        for user in CustomUser.objects.all():
            if user.has_perm('turnos_app.es_paciente') and not user.has_perm('turnos_app.es_administrador'): # Esta consulta es debido a que el admin es considerado recepcionista tambien
                lista_pacientes.append(user)
        context['lista_pacientes'] = lista_pacientes
        return context

class EliminarPacienteView(PermissionRequiredMixin, DeleteView):
    
    login_url = ADMINISTRADOR_LOGIN_URL
    model = CustomUser
    permission_required = ('turnos_app.es_administrador')
    template_name = 'administrador/eliminar_usuario.html'

    def delete(self, request, *args, **kwargs):
        user = self.get_object()
        perfil = Paciente.objects.get(user=user)
        obra_social = perfil.obra_social
        if obra_social != None:
            obra_social.pacientes -= 1
            obra_social.save()
        user.delete()
        messages.info(request, 'Paciente eliminado con éxito!')
        return redirect('menu-pacientes')

class EspecialidadCreate(PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    
    login_url = ADMINISTRADOR_LOGIN_URL
    model = Especialidad
    fields = ['nombre']
    template_name = 'administrador/crear_especialidad.html'
    permission_required = ('turnos_app.es_administrador')
    success_url = reverse_lazy('crear-especialidad')
    success_message = "Especialidad creada con éxito."

class EspecialidadDelete(PermissionRequiredMixin, SuccessMessageMixin, DeleteView):

    login_url = ADMINISTRADOR_LOGIN_URL
    model = Especialidad
    template_name = 'administrador/eliminar_especialidad.html'
    permission_required = ('turnos_app.es_administrador')

    def delete(self, request, *args, **kwargs):
        especialidad = self.get_object()
        if especialidad.medicos > 0:
            messages.warning(request, 'La especialidad no puede ser eliminada debido a que contiene medicos.')
            return redirect('menu-especialidades')
        else:
            messages.info(request, 'Especialidad eliminada con éxito!')
            especialidad.delete()
            return redirect('menu-especialidades')

class EspecialidadListView(PermissionRequiredMixin, ListView):

    login_url = ADMINISTRADOR_LOGIN_URL
    model = Especialidad
    template_name = 'administrador/lista_especialidades.html'
    permission_required = ('turnos_app.es_administrador')    

class ObraSocialCreate(PermissionRequiredMixin, SuccessMessageMixin, CreateView):

    login_url = ADMINISTRADOR_LOGIN_URL
    model = ObraSocial
    fields = ['nombre']
    template_name = 'administrador/crear_obra_social.html'
    permission_required = ('turnos_app.es_administrador')
    success_url = reverse_lazy('crear-obra-social')
    success_message = "Obra Social creada con éxito."
    
class ObraSocialDelete(PermissionRequiredMixin, SuccessMessageMixin, DeleteView):

    login_url = ADMINISTRADOR_LOGIN_URL
    model = ObraSocial
    template_name = 'administrador/eliminar_obra_social.html'
    permission_required = ('turnos_app.es_administrador')

    
    def delete(self, request, *args, **kwargs):
        obra_social = self.get_object()
        if obra_social.pacientes > 0:
            messages.warning(request, 'La Obra Social no puede ser eliminada debido a que contiene pacientes.')
            return redirect('menu-obras-sociales')
        else:
            messages.info(request, 'Obra Social eliminada con éxito!')
            obra_social.delete()
            return redirect('menu-obras-sociales')
    
class ObraSocialListView(PermissionRequiredMixin, ListView):

    login_url = ADMINISTRADOR_LOGIN_URL
    model = ObraSocial
    template_name = 'administrador/lista_obras_sociales.html'
    permission_required = ('turnos_app.es_administrador')

def get_especialidades_data(request, *args, **kwargs):
    data = {}
    for especialidad in Especialidad.objects.all():
        data[especialidad.nombre] = especialidad.medicos
    return JsonResponse(data)

def get_obras_sociales_data(request, *args, **kwargs):
    data = {}
    for obra_social in ObraSocial.objects.all():
        data[obra_social.nombre] = obra_social.medicos
    return JsonResponse(data)

class EstadisticasView(PermissionRequiredMixin, View):

    login_url = ADMINISTRADOR_LOGIN_URL
    permission_required = ('turnos_app.es_administrador')

    def get(self, request, *args, **kwargs):
        return render(request, 'administrador/estadisticas.html', {})

class ChartEstadisticas(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, format=None):
        especialidades = []
        obras_sociales = []
        medicos = []
        pacientes = []
        for especialidad in Especialidad.objects.all():
            especialidades.append(especialidad.nombre)
            medicos.append(especialidad.medicos)
        for obra_social in ObraSocial.objects.all():
            obras_sociales.append(obra_social.nombre)
            pacientes.append(obra_social.pacientes)            
        data = {
            "especialidades": especialidades,
            "medicos": medicos,
            "obras_sociales": obras_sociales,
            "pacientes": pacientes,
        }
        return Response(data)

