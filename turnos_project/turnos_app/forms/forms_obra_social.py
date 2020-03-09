from django.forms import ModelForm
from turnos_app.models import ObraSocial

class ObraSocialForm(ModelForm):
    class Meta:
        model = ObraSocial
        fields=['nombre']