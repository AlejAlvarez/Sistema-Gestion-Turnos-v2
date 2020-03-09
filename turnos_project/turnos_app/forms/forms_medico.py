from django import forms
from django.forms import models
from django.db import transaction

from .user_forms import CustomUserCreationForm, CustomUserChangeForm
from ..models import CustomUser, Medico, Especialidad


class MedicoCreationForm(CustomUserCreationForm):

    cuil = forms.IntegerField()
    especialidad = forms.ModelChoiceField(
        queryset=Especialidad.objects.all(),
        required=True
    )

class MedicoChangeForm(models.ModelForm):
    
    class Meta:
        model = Medico
        fields = ('cuil', 'especialidad')