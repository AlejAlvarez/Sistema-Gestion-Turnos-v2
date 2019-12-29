from django import forms
from django.forms import ModelForm
from ..models import CustomUser

class RecepcionistaInformationForm(ModelForm):

    class Meta:
        model = CustomUser
        fields = ['first_name','last_name','username','last_login']
        atrs = {
            'class': 'form-control',
            'id': 'disabledInput',
            'disabled': True            
        }
        widgets = {
            'first_name': forms.TextInput(
                attrs = atrs
            ),
            'last_name': forms.TextInput(
                attrs = atrs
            ),
            'username': forms.TextInput(
                attrs = atrs
            ),
            'last_login': forms.TextInput(
                attrs = atrs
            )
        }