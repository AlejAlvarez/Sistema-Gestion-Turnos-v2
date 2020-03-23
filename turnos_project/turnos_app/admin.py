from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms.user_forms import CustomUserCreationForm, CustomUserChangeForm
from .models import *


# Register your models here.

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser

    fieldsets = UserAdmin.fieldsets + ((None, {'fields': ('documento','nacimiento','domicilio','telefono')}),)

    list_display = ['pk', 'username', 'email', 'is_staff']

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Medico)
admin.site.register(Paciente)
admin.site.register(Especialidad)
admin.site.register(ObraSocial)
admin.site.register(Turno)
admin.site.register(TurnoCancelado)
admin.site.register(TurnoAtendido)
admin.site.register(DiaLaboral)
admin.site.register(HorarioLaboral)