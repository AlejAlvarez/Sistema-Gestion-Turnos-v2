from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.forms import models
from django.db import transaction

from ..models import CustomUser, Medico
from app_informacion.models import Especialidad


class MedicoCreationForm(UserCreationForm):

    cuil = forms.IntegerField()
    especialidad = forms.ModelChoiceField(
        queryset=Especialidad.objects.all(),
        widget=forms.RadioSelect,
        required=True
    )

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

#    @transaction.atomic
#    def save(self):
#        user = super().save(commit=False)
#        user.user_type = 
#        user.save()
#        student = Student.objects.create(user=user)
#        student.interests.add(*self.cleaned_data.get('interests'))
#        return user

