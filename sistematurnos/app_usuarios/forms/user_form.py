from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.forms import models

from ..models import CustomUser

class CustomUserCreationForm(UserCreationForm):

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = (
            'first_name',
            'last_name',
            'documento',
            'domicilio',
            'telefono',
            'nacimiento',
            'email',
            'username',
            'password1',
            'password2', 
        )
        labels = {
            'first_name': 'Nombre',
            'last_name': 'Apellido',
            'username': 'Usuario',
        }
    
class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = CustomUser
        fields = (
            'first_name',
            'last_name',
            'documento',
            'domicilio',
            'telefono',
            'nacimiento',
            'email',
            'username', 
        )
        labels = {
            'first_name': 'Nombre',
            'last_name': 'Apellido',
            'username': 'Usuario',
        }
        
