from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms.user_form import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser, Medico, Paciente
from app_informacion.models import Especialidad, ObraSocial
from app_turnos.models import Turno, DiaLaboral, HorarioLaboral

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser

    list_display = ['pk', 'username', 'email', 'is_staff']

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Medico)
admin.site.register(Paciente)
admin.site.register(Especialidad)
admin.site.register(ObraSocial)
admin.site.register(Turno)
admin.site.register(DiaLaboral)
admin.site.register(HorarioLaboral)