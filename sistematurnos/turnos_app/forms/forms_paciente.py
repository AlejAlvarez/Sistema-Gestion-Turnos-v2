from django import forms
from django.forms import models
from ..models import Paciente
# formularios que va a utilizar el usuario Paciente


class PacienteChangeForm(models.ModelForm):
    
    class Meta:
        model = Paciente
        fields = ('genero', 'obra_social')