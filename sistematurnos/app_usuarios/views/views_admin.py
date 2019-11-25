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
        return super().post(request, *args, **kwargs)

# debería tener permisos de superusuario
class UpdateAdminView(CustomUserUpdateView):

    def get(self, request, pk):
        usuario = get_object_or_404(CustomUser, pk=pk)
        return super().get(request, pk)

class AdminDetailView(DetailView):
    model = CustomUser
    template_name = 'usuarios/detail.html'