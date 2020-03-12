from django.forms import ModelForm
from turnos_app.models import Especialidad

class EspecialidadForm(ModelForm):
    class Meta:
        model = Especialidad
        fields = ['nombre']