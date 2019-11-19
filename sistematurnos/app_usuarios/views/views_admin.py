from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import DetailView

from ..models import CustomUser
from ..forms.user_form import CustomUserCreationForm, CustomUserChangeForm
from .views_user import CustomUserCreateView, CustomUserUpdateView

class SignUpAdminView(CustomUserCreateView):

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
        
    def post(self, request, *args, **kwargs):
        kwargs['user_type'] = 4 # 4 es de Administrador
        kwargs['is_staff'] = True
        kwargs['is_superuser'] = True # parece ser que solo permite esto cuando se crea de consola con el createsuperuser
        return super().post(request, *args, **kwargs)

class UpdateAdminView(CustomUserUpdateView):

    def get(self, request, pk):
        usuario = get_object_or_404(CustomUser, pk=pk)
        
        if(usuario.user_type == 4):
            return super().get(request, pk)
        else:
            return HttpResponse('El usuario buscado no corresponde a un administrador')

class AdminDetailView(DetailView):
    model = CustomUser
    template_name = 'usuarios/detail.html'
