from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser
from .forms.user_form import CustomUserCreationForm, CustomUserChangeForm
from app_informacion.models import Especialidad, ObraSocial

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser

    list_display = ['pk', 'username', 'email', 'user_type', 'is_staff']

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Especialidad)
admin.site.register(ObraSocial)