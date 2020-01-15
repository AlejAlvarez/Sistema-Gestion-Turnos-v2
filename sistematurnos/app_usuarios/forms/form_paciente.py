from django import forms
from django.forms import models

from .user_form import CustomUserCreationForm, CustomUserChangeForm
from ..models import CustomUser, Paciente
from app_turnos.forms import set_all_widgets_bootstrap_class
from app_informacion.models import ObraSocial

class PacienteCreationForm(CustomUserCreationForm):

    genero = forms.ChoiceField(choices=Paciente.GENERO_CHOICES, widget=forms.RadioSelect)
    obra_social = forms.ModelChoiceField(
        queryset=ObraSocial.objects.all(),
        required=False
    )

    def __init__(self, *args, **kwargs):
        super(PacienteCreationForm, self).__init__(*args, **kwargs)
        set_all_widgets_bootstrap_class(self.fields)
        self.fields['nacimiento'].widget.attrs.update({
            'class':'form-control snps-inline-select'
        })
        self.fields['genero'].widget.attrs['class'] = "form-check-input"

class PacienteChangeForm(models.ModelForm):
    
    class Meta:
        model = Paciente
        fields = ('genero', 'obra_social')

