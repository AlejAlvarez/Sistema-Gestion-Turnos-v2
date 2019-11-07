from django.urls import path, include

from .views import *
from .views.views_admin import *
from .views.views_medico import *
from .views.views_paciente import *
from .views.views_recepcionista import *

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
]