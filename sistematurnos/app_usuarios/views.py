from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView

from .models import CustomUser
from .forms.user_form import CustomUserCreationForm 
from .forms.form_medico import MedicoCreationForm

def exampleView(request):
    return HttpResponse('Pagina de usuarios')

class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'

class SignUpMedicoView(CreateView):
    form_class = MedicoCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'