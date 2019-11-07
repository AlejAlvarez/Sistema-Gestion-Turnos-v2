from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView 
from django.contrib.auth.mixins import LoginRequiredMixin

from ..models import CustomUser
from ..forms.user_form import CustomUserCreationForm, CustomUserChangeForm

class CustomUserCreateView(LoginRequiredMixin, CreateView):
    login_url = 'login'
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class()

        return render(request, self.template_name, {'form': form})
        
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
                                                documento=documento, domicilio=domicilio, nacimiento=nacimiento, telefono=telefono,
                                                **kwargs)

            user.save()
            return HttpResponse('Usuario del tipo %s creado con éxito' % dict(CustomUser.USER_TYPE_CHOICES).get(kwargs['user_type']))
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
        
#    def get(self, request, pk):
#        user = CustomUser.objects.get(pk=pk)
#
#        return render(request, self.template_name, {'form':self.form_class})
#    
#    def post(self, request, pk):
#        form = self.form_class
#
#        if form.is_valid():
#            user = CustomUser.objects.get(pk=pk)
#
#            user.username   = form.cleaned_data.get('username')
#            user.password   = form.cleaned_data.get('password1')
#            user.email      = form.cleaned_data.get('email')
#            user.first_name = form.cleaned_data.get('first_name')
#            user.last_name  = form.cleaned_data.get('last_name')
#            user.documento  = form.cleaned_data.get('documento')
#            user.domicilio  = form.cleaned_data.get('domicilio')
#            user.nacimiento = form.cleaned_data.get('nacimiento')
#            user.telefono   = form.cleaned_data.get('telefono')
#
#            user.save()
#
#            return HttpResponse('%s editado con éxito' % dict(CustomUser.USER_TYPE_CHOICES).get(kwargs['user_type']))
#        else:
#            return self.form_invalid(form)
