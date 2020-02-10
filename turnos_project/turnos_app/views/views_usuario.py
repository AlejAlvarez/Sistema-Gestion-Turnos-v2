from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView 
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import Permission
from django.core.exceptions import PermissionDenied
from ..forms.user_forms import CustomUserCreationForm, CustomUserChangeForm
from django.core.exceptions import PermissionDenied
from django.contrib.auth import authenticate, login
from ..models import CustomUser
from ..models import *

def loguear_usuario(request):
    default_get_view = reverse_lazy('home')
    print(request.method)
    if request.method == 'POST':   
        username = request.POST['username']
        password = request.POST['password'] 
        rol = request.POST['rol']
        user = authenticate(username=username,password=password)
        if user is not None:
            login(request,user)
            user_perm = 'turnos_app.es' + '_' + rol
            accept_view_name = 'index' + '-' + rol
            reject_view_name = 'login' + '-' + rol
            if (user.has_perm(user_perm)):
                return redirect(accept_view_name)
            else: 
                return redirect(reject_view_name) 
        else: 
            return HttpResponse('No se pudo autenticar')   
    else:
        return redirect(default_get_view)

class CustomUserCreateView(LoginRequiredMixin, CreateView):
    login_url = 'login'
    form_class = CustomUserCreationForm
    template_name = 'registration/signup.html'

    # verificar si el usuario que solicita la página es el que está logueado
    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    # los permisos estarán definidos a través de los kwargs    
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if(form.is_valid()):
            username   = form.cleaned_data.get('username')
            contrasena = form.cleaned_data.get('password1')
            email      = form.cleaned_data.get('email')
            nombre     = form.cleaned_data.get('first_name')
            apellido   = form.cleaned_data.get('last_name')
            documento  = form.cleaned_data.get('documento')
            domicilio  = form.cleaned_data.get('domicilio')
            nacimiento = form.cleaned_data.get('nacimiento')
            telefono   = form.cleaned_data.get('telefono')

            user = CustomUser.objects.create_user(username, email, contrasena, first_name=nombre, last_name=apellido,
                                                documento=documento, domicilio=domicilio, nacimiento=nacimiento, telefono=telefono)            
            # adding permission
            user_role_permission = Permission.objects.get(codename=kwargs['user_permission_codename'])
            user.user_permissions.add(user_role_permission)            

            user.save()
            return HttpResponse('Usuario del tipo %s creado con éxito' % user_role_permission.name)
        else:
            return render(request, self.template_name, {'form': form})
    
    def set_form_class(self, form_class):
        self.form_class = form_class

class CustomUserUpdateView(LoginRequiredMixin, UpdateView):
    login_url = 'login'
    model = CustomUser
    template_name = 'usuarios/update_user.html'
    form_class = CustomUserChangeForm
    success_url = 'app_informacion:home'

    def set_form_class(self, form_class):
        self.form_class = form_class

    def get_form_class(self):
        return self.form_class
