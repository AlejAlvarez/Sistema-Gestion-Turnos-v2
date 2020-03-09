from django import forms
from django.forms import models
from .user_forms import CustomUserCreationForm, CustomUserChangeForm
from ..models import CustomUser,Paciente, ObraSocial

# formularios que va a utilizar el usuario Recepcionista

class RecepcionistaInformationForm(forms.ModelForm):

    class Meta:
        model = CustomUser
        fields = ['first_name','last_name','username','last_login']

    # método para aplicar atributos a todos los widgets
    def __init__(self,*args,**kwargs):
        super(RecepcionistaInformationForm,self).__init__(*args,**kwargs)


class DocumentoForm(forms.Form):
    
    documento = forms.IntegerField()