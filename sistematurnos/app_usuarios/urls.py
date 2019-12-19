from django.urls import path, include
from django.contrib.auth import views as auth_views

from .views import *
from .views.views_user import *
from .views.views_admin import *
from .views.views_medico import *
from .views.views_paciente import *
from .views.views_recepcionista import *
from .views.redirect_views import log_user

app_name = 'app_usuarios'

urlpatterns = [
    path('registrar-admin/', SignUpAdminView.as_view(), name='registrar_admin'),
    path('registrar-recep/', SignUpRecepcionistaView.as_view(), name='registrar_recepcionista'),
    path('registrar-medico/', SignUpMedicoView.as_view(), name='registrar_medico'),
    path('registrar-paciente/', SignUpPacienteView.as_view(), name='registrar_paciente'),
    path('editar-admin/<int:pk>/', UpdateAdminView.as_view(), name='editar-admin'),
    path('editar-recep/<int:pk>/', UpdateRecepcionistaView.as_view(), name='editar-recep'),
    path('editar-paciente/<int:pk>/', editar_paciente, name='editar-paciente'),
    path('editar-medico/<int:pk>/', editar_medico, name='editar-medico'),
    path('log-user',log_user,name="log-user"),
    path('paciente/perfil/',perfil_paciente,name="perfil-paciente"),
    path('login/', auth_views.LoginView.as_view(), name='login'),
]