from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import ListView
from django.views.generic.edit import CreateView, UpdateView 

from shapeshifter.views import MultiFormView

from ..models import CustomUser, Paciente
from ..forms.form_paciente import PacienteCreationForm, PacienteChangeForm
from app_informacion.models import ObraSocial
from .views_user import CustomUserCreateView, CustomUserUpdateView
from ..forms.user_form import CustomUserChangeForm

class SignUpPacienteView(CustomUserCreateView):
    form_class = PacienteCreationForm
    success_url = reverse_lazy('login')
    #template_name = 'registration/signup.html'

    def get(self, request, *args, **kwargs): 

        return super().get(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        form = PacienteCreationForm(request.POST)
        if(form.is_valid()):
            print('Entrando al is_valid(), previo a llamada super()')
            kwargs['user_type'] = 1 # 1 es para el paciente
            kwargs['is_staff'] = False
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

def editar_paciente(request, pk):

    user = get_object_or_404(CustomUser, pk=pk)

    if(user.user_type == 1):

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
            form = CustomUserChangeForm(instance=user)
            paciente_form = PacienteChangeForm(instance=user.paciente)
            args = {'form': form, 'perfil_form': paciente_form}
            return render(request, 'usuarios/update_user_mform.html', args)
    else:
        return HttpResponse('El usuario buscado no corresponde a un paciente')

#    model = Paciente
#    template_name = 'update_user.html'
#    form_class = PacienteChangeForm
#
#    def get(self, request, pk):
#        usuario = get_object_or_404(CustomUser, pk=pk)
#
#        if(usuario.user_type == 1):
#            perfil_paciente = get_object_or_404(Paciente, user=usuario)
#
#            return super().get(request, pk)
#        else:
#            return HttpResponse('El usuario buscado no corresponde a un paciente')
#    
#    def post(self, request, pk):
#        form = PacienteChangeForm(request.POST)
#
#        if form.is_valid():
#            super().post(request, pk)
#            usuario = get_object_or_404(CustomUser, pk=pk)
#            perfil_paciente = Paciente.objects.get(user=usuario)
#            obra_social_seleccionada = ObraSocial.objects.get(nombre=form.cleaned_data['obra_social'])
#            perfil_paciente.obra_social = obra_social_seleccionada
#            perfil_paciente.genero = form.cleaned_data['genero']
#
#            perfil_paciente.save()
#
#            return HttpResponse('Paciente editado con exito')
#        
#        else:
#            return self.form_invalid(form)

