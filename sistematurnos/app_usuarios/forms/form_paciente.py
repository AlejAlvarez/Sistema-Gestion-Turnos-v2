from django import forms
from django.forms import models

from .user_form import CustomUserCreationForm, CustomUserChangeForm
from ..models import CustomUser, Paciente

from app_informacion.models import ObraSocial

class PacienteCreationForm(CustomUserCreationForm):

    genero = forms.ChoiceField(choices=Paciente.GENERO_CHOICES, widget=forms.RadioSelect)
    obra_social = forms.ModelChoiceField(
        queryset=ObraSocial.objects.all(),
        required=False
    )

class PacienteChangeForm(models.ModelForm):
    
    class Meta:
        model = Paciente
        fields = ('genero', 'obra_social')
    #genero = forms.ChoiceField(choices=Paciente.GENERO_CHOICES, widget=forms.RadioSelect)
    #obra_social = forms.ModelChoiceField(
    #    queryset=ObraSocial.objects.all(),
    #    required=False
    #)

