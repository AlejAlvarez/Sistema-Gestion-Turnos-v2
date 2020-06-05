from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.forms import models
from crispy_forms.helper import FormHelper

from ..models import CustomUser

ANOS_NACIMIENTO_CHOICES = range(1920, 2020)

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
            'email': 'Correo Electrónico',
        }
        widgets = {
            'nacimiento': forms.SelectDateWidget(
                years=ANOS_NACIMIENTO_CHOICES,
                attrs={'class':'nacimiento-form'})
        }
        help_texts = {
            'documento': 'Número de documento de 8 dígitos',
            'nacimiento': 'Fecha de nacimiento. Formato MM/DD/AAAA'
        }
    
    def __init__(self, *args, **kwargs):
        super(CustomUserCreationForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)

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
            'email': 'Correo Electrónico',
        }
        widgets = {
            'nacimiento': forms.SelectDateWidget(
                years=ANOS_NACIMIENTO_CHOICES,
                attrs={'class':'nacimiento-form'})
        }
        help_texts = {
            'documento': 'Número de documento de 8 dígitos',
            'nacimiento': 'Fecha de nacimiento. Formato MM/DD/AAAA'
        }