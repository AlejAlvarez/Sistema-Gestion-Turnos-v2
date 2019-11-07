from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView

from ..models import CustomUser
from ..forms.user_form import CustomUserCreationForm, CustomUserChangeForm
from .views_user import CustomUserCreateView, CustomUserUpdateView

class SignUpRecepcionistaView(CustomUserCreateView):
    #form_class = CustomUserCreationForm
    #success_url = reverse_lazy('login')
    #template_name = 'registration/signup.html'

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
        
    def post(self, request, *args, **kwargs):
        kwargs['user_type'] = 2 # 2 es de recepcionista
        kwargs['is_staff'] = True
        return super().post(request, *args, **kwargs)

class UpdateRecepcionistaView(CustomUserUpdateView):
#    form_class = CustomUserChangeForm
#    model = CustomUser
#    template_name = 'update_user.html'

    def get(self, request, pk):
        usuario = get_object_or_404(CustomUser, pk=pk)
        
        if(usuario.user_type == 2):
            return super().get(request, pk)
        else:
            return HttpResponse('El usuario buscado no corresponde a un recepcionista')