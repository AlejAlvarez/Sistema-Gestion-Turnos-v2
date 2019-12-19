from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import ListView
from django.views.generic.edit import CreateView, UpdateView 

from ..models import CustomUser, Paciente
from ..forms.form_paciente import PacienteCreationForm, PacienteChangeForm
from app_informacion.models import ObraSocial
from .views_user import CustomUserCreateView, CustomUserUpdateView
from ..forms.user_form import CustomUserChangeForm
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import Permission
from .views_user import check_ownership_or_403

class SignUpPacienteView(PermissionRequiredMixin, CustomUserCreateView):
    form_class = PacienteCreationForm
    success_url = reverse_lazy('login')
    #template_name = 'registration/signup.html'
    # being an admin, you have all permissions required to access every url in the system
    permission_required = ('login_required','app_usuarios.es_recepcionista')

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


@login_required
def editar_paciente(request, pk):

    user = get_object_or_404(CustomUser, pk=pk)

    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, instance=user)
        paciente_form = PacienteChangeForm(request.POST, instance=user.paciente)

        if form.is_valid() and paciente_form.is_valid():
            user = form.save()
            paciente = paciente_form.save(False)
            paciente.user = user
            paciente.save()
            return redirect('app_informacion:home')        
    else:
        if (viewing_user.has_perm('app_usuarios.es_recepcionista') or (viewing_user.has_perm('app_usuarios.es_paciente'))):
            all_permissions = list(Permission.objects.filter(user=viewing_user.pk))  
            print(all_permissions) 
            if (viewing_user.has_perm('app_usuarios.es_paciente')):
                print("---------- USER ES PACIENTE ----------")
                check_ownership_or_403(request,pk)
        form = CustomUserChangeForm(instance=user)
        paciente_form = PacienteChangeForm(instance=user.paciente)
        args = {'form': form, 'perfil_form': paciente_form}
        return render(request, 'usuarios/update_user_mform.html', args)

# va a retornar el user que estÃ¡ logueado
@login_required
def perfil_paciente(request):
    user_pk = request.user.pk
    paciente_user = get_object_or_404(CustomUser,pk=user_pk)
    args = {'paciente_user': paciente_user}
    return render(request, 'usuarios/paciente_profile.html', args)

