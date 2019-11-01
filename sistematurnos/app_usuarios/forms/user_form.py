from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from ..models import CustomUser
from django.forms import models

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
    
    #@transaction.atomic
    #def save(self, *args, **kwargs):       
    #   user = super().save(commit=False)
    #   user.
    
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
            'first_name': 'nombre',
            'last_name': 'apellido',
            'username': 'usuario',
        }
