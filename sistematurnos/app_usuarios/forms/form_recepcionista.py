from django import forms
from django.forms import ModelForm
from ..models import CustomUser

class RecepcionistaInformationForm(ModelForm):

    class Meta:
        model = CustomUser
        fields = ['first_name','last_name','username','last_login']

    # método para aplicar atributos a todos los widgets
    def __init__(self,*args,**kwargs):
        super(RecepcionistaInformationForm,self).__init__(*args,**kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({
            'id': 'disabledInput',
            'disabled': True,
            'class': 'form-control'
            })