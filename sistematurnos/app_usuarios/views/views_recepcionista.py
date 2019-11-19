from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import  ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView

from ..models import CustomUser
from ..forms.user_form import CustomUserCreationForm, CustomUserChangeForm
from .views_user import check_ownership_or_403 ,CustomUserCreateView, CustomUserUpdateView
from django.contrib.auth.mixins import PermissionRequiredMixin

<<<<<<< Updated upstream
class SignUpRecepcionistaView(PermissionRequiredMixin,CustomUserCreateView):
=======

class SignUpRecepcionistaView(PermissionRequiredMixin,CustomUserCreateView):
    #form_class = CustomUserCreationForm
    #success_url = reverse_lazy('login')
    #template_name = 'registration/signup.html'
>>>>>>> Stashed changes
    permission_required = ('login_required','is_staff','is_superuser')

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
        
    def post(self, request, *args, **kwargs):
<<<<<<< Updated upstream
        kwargs['user_permission_codename'] = 'es_recepcionista'
        return super().post(request, *args, **kwargs)

class UpdateRecepcionistaView(PermissionRequiredMixin,CustomUserUpdateView):
    permission_required = ('login_required','app_usuarios.is_recepcionist')
    
=======
        kwargs['user_permission_codename'] = 'is_recepcionist'
        return super().post(request, *args, **kwargs)


class UpdateRecepcionistaView(PermissionRequiredMixin,CustomUserUpdateView):

    permission_required = ('login_required','app_usuarios.is_recepcionist')

>>>>>>> Stashed changes
    def get(self, request, pk):
        usuario = get_object_or_404(CustomUser, pk=pk)