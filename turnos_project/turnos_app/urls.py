from django.urls import path,include, re_path

from django.contrib.auth import views as auth_views
from .views.page_views import *
from .views.views_usuario import *
from .views.views_paciente import *
from .views.views_recepcionista import *
from .views.views_medico import *
from .views.ajax_views import *

urlpatterns = [

    # general

    path('',home,name='home'),
    path('loguear-usuario',loguear_usuario,name='loguear-usuario'),

    # recepcionista patterns

    path('recepcionista/login',auth_views.LoginView.as_view(template_name='recepcionista/login.html'),name='login-recepcionista'),
    path('recepcionista/logout',auth_views.LogoutView.as_view(template_name='recepcionista/logout.html'),name='logout-recepcionista'),
    path('recepcionista/index/',index_recepcionista,name='index-recepcionista'),
    path('recepcionista/gestionar-turnos/',gestionar_turnos,name='gestionar-turnos'),
    path('recepcionista/registrar-paciente/',SignUpPacienteView.as_view(),name='registrar-paciente'),
    path('recepcionista/reservar-turno/',reservar_turno,name='reservar-turno'),
    path('recepcionista/reservar-turno/<int:pk>/',completar_reserva,name='completar-reserva'),
    path('recepcionista/ajax/buscar-turnos',ConsultarTurnosEspecialidadAjax.as_view(),name='consultar-turnos-especialidad-ajax'),
    
    # medico patterns
    
    #path('medico/index',index_medico,'index-medico'),
    #path('medico/ver-turnos',ver_turnos,'ver-turnos'),
    #path('medico/atender-turno/<int:pk>',atender_turno,'atender-turno'),
    #path('medico/actualizar-horarios',actualizar_horarios,'actualizar-horarios'),
    #path('medico/crear-turnos')
    
    # paciente patterns

    path('paciente/login/',auth_views.LoginView.as_view(template_name='paciente/login.html'),name='login-paciente'),
    path('paciente/logout/',auth_views.LogoutView.as_view(template_name='paciente/logout.html'),name='logout-paciente'),
    path('paciente/index/',index_paciente,name='index-paciente'),
    path('paciente/buscar-turnos/',buscar_turnos,name='hacer-reserva'),
    path('paciente/confirmar-reserva/<int:pk>',reservar_turno_paciente,name='confirmar-reserva'),
    path('paciente/ver-turno/<int:pk>',VerTurno.as_view(),name='ver-turno'),
    path('paciente/cancelar-turno/<int:pk>',cancelar_turno,name='cancelar-turno'),
    path('paciente/historial',ver_historial,name='ver-historial'),
    path('paciente/mis-turnos',ListarTurnos.as_view(),name='mis-turnos'),
    path('paciente/buscar-turnos',buscar_turnos,name='buscar-turnos'),
    path('paciente/ajax/filtrar-medicos',BuscarMedicosAjax.as_view(),name='filtrar-medicos-ajax'),
    path('paciente/ajax/buscar-turnos',BuscarTurnosAjax.as_view(),name='buscar-turnos-ajax'),
    #path('paciente/editar/<int:pk>/',editar_paciente, name='editar-paciente'),
]