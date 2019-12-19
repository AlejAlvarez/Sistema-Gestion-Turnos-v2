from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView

from ..models import CustomUser, Medico
from ..forms.form_medico import MedicoCreationForm, MedicoChangeForm 
from ..forms.user_form import CustomUserChangeForm
from app_informacion.models import Especialidad
from .views_user import CustomUserCreateView, CustomUserUpdateView
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import Permission
from .views_user import check_ownership_or_403

class SignUpMedicoView(PermissionRequiredMixin, CustomUserCreateView):
    form_class = MedicoCreationForm
    success_url = reverse_lazy('login')
    #template_name = 'registration/signup.html'
    permission_required = ('login_required','is_staff','is_superuser')

    def get(self, request, *args, **kwargs):

        return super().get(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        form = MedicoCreationForm(request.POST)
        if(form.is_valid()):
            kwargs['user_permission_codename'] = 'es_medico'
            super().post(request, *args, **kwargs)

            user = CustomUser.objects.get(documento=form.c0leaned_data.get('documento'))
            cuil = form.cleaned_data.get('cuil')
            especialidad_seleccionada = Especialidad.objects.get(nombre=form.cleaned_data['especialidad'])
            perfil_medico = Medico.objects.create(user=user, cuil=cuil, especialidad=especialidad_seleccionada)
            perfil_medico.save()

            return HttpResponse('Exito creando medico')
        else:
            print('Error de validacion de formulario')
            return super().get(request, *args, **kwargs)

@login_required
@permission_required('app_usuarios.es_medico')                    
def editar_medico(request, pk):

    user = get_object_or_404(CustomUser, pk=pk)

    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, instance=user)
        medico_form = MedicoChangeForm(request.POST, instance=user.medico)

        if form.is_valid() and medico_form.is_valid():
            user = form.save()
            medico = medico_form.save(False)
            medico.user = user
            medico.save()
            return redirect('app_informacion:home')
    
    else:
        # lanza un permissiondenied si no es el paciente correcto
        if user.has_perm('app_usuarios.es_medico'):   
            check_ownership_or_403(request,pk)
        form = CustomUserChangeForm(instance=user)
        medico_form = MedicoChangeForm(instance=user.medico)
        args = {'form': form, 'perfil_form': medico_form}
        return render(request, 'usuarios/update_user_mform.html', args)
