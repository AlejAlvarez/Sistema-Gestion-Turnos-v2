from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from app_informacion.models import Especialidad
from .models import CustomUser
from .forms.user_form import CustomUserCreationForm, CustomUserChangeForm

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Especialidad)