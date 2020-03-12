from django.urls import path,include, re_path

from django.contrib.auth import views as auth_views
from .views.page_views import *
from .views.views_usuario import *
from .views.views_paciente import *
from .views.views_recepcionista import *
from .views.views_medico import *
from .views.views_administrador import *
from .views.ajax_views import *

urlpatterns = [

    # general

    path('',home,name='home'),

    # recepcionista patterns

    path('recepcionista/login/',LoginRecepcionistaView.as_view(),name='login-recepcionista'),
    path('recepcionista/logout/',logout_usuario,name='logout-recepcionista'),
    path('recepcionista/',index_recepcionista,name='index-recepcionista'),
    path('recepcionista/gestionar-turnos/',gestionar_turnos,name='gestionar-turnos'),
    path('recepcionista/registrar-paciente/',SignUpPacienteView.as_view(),name='registrar-paciente'),
    path('recepcionista/reservar-turno/',ReservarTurnoView.as_view(),name='reservar-turno'),
    path('recepcionista/completar-reserva/<int:pk>/',CompletarReservaView.as_view(),name='completar-reserva'),
    path('recepcionista/ajax/buscar-turnos/',ConsultarTurnosEspecialidadAjax.as_view(),name='consultar-turnos-especialidad-ajax'),
    path('recepcionista/ajax/obtener-paciente/',ObtenerPacienteAjax.as_view(),name='obtener-paciente-ajax'),
    
    # medico patterns
    
    #path('medico/index',index_medico,'index-medico'),
    #path('medico/ver-turnos',ver_turnos,'ver-turnos'),
    #path('medico/atender-turno/<int:pk>',atender_turno,'atender-turno'),
    #path('medico/actualizar-horarios',actualizar_horarios,'actualizar-horarios'),
    #path('medico/crear-turnos')
    
    # paciente patterns

    path('paciente/login/',LoginPacienteView.as_view(),name='login-paciente'),
    path('paciente/logout/',logout_usuario,name='logout-paciente'),
    path('paciente/',index_paciente,name='index-paciente'),
    path('paciente/buscar-turnos/',buscar_turnos,name='buscar-turnos'),
    path('paciente/confirmar-reserva/<int:pk>/',reservar_turno_paciente,name='confirmar-reserva'),
    path('paciente/ver-turno/<int:pk>/',VerTurno.as_view(),name='ver-turno'),
    path('paciente/cancelar-turno/<int:pk>/',cancelar_turno,name='cancelar-turno'),
    path('paciente/historial/',ver_historial,name='ver-historial'),
    path('paciente/mis-turnos/',ListarTurnos.as_view(),name='turnos-paciente'),
    path('paciente/ajax/filtrar-medicos/',BuscarMedicosAjax.as_view(),name='filtrar-medicos-ajax'),
    path('paciente/ajax/buscar-turnos/',BuscarTurnosAjax.as_view(),name='buscar-turnos-ajax'),
    #path('paciente/editar/<int:pk>/',editar_paciente, name='editar-paciente'),

    # administrador patterns

    path('administrador/login/', LoginAdministradorView.as_view(), name='login-administrador'),
    path('administrador/logout/',logout_usuario,name='logout-administrador'),
    path('administrador/', index_administrador,name='index-administrador'),
    path('administrador/menu-recepcionistas/', RecepcionistaListView.as_view(), name='menu-recepcionistas'),
    path('administrador/registrar-recepcionista/', SignUpRecepcionistaView.as_view(), name='registrar-recepcionista'),
    path('administrador/editar-recepcionista/<int:pk>/', editar_informacion_recepcionista, name='editar-recepcionista'),
    path('administrador/ver-recepcionista/<int:pk>/', DetailsRecepcionista.as_view(), name='ver-recepcionista'),
    path('administrador/eliminar-recepcionista/<int:pk>/', EliminarRecepcionistaView.as_view(), name='eliminar-recepcionista'),
    path('administrador/menu-medicos/', MedicoListView.as_view(), name='menu-medicos'),
    path('administrador/registrar-medico/', SignUpMedicoView.as_view(), name='registrar-medico'),
    path('administrador/editar-medico/<int:pk>/', editar_informacion_medico, name='editar-medico'),
    path('administrador/ver-medico/<int:pk>/', DetailsMedico.as_view(), name='ver-medico'),
    path('administrador/eliminar-medico/<int:pk>/', EliminarMedicoView.as_view(), name='eliminar-medico'),
    path('administrador/menu-administradores/', AdministradorListView.as_view(), name='menu-administradores'),
    path('administrador/registrar-administrador/', SignUpAdministradorView.as_view(), name='registrar-administrador'),
    path('administrador/editar-administrador/<int:pk>/', editar_informacion_administrador, name='editar-administrador'),
    path('administrador/ver-administrador/<int:pk>/', DetailsAdministrador.as_view(), name='ver-administrador'),
    path('administrador/eliminar-administrador/<int:pk>/', EliminarAdministradorView.as_view(), name='eliminar-administrador'),
    path('administrador/menu-pacientes/', PacienteListView.as_view(), name='menu-pacientes'),
    path('administrador/menu-pacientes/eliminar-paciente/<int:pk>/', EliminarPacienteView.as_view(), name='eliminar-paciente'),
    path('administrador/menu-especialidades/', EspecialidadListView.as_view(), name='menu-especialidades'),
    path('administrador/crear-especialidad/', EspecialidadCreate.as_view(), name='crear-especialidad'),
    path('administrador/menu-especialidades/eliminar-especialidad/<int:pk>/', EspecialidadDelete.as_view(), name='eliminar-especialidad'),
    path('administrador/menu-obras-sociales/', ObraSocialListView.as_view(), name='menu-obras-sociales'),
    path('administrador/crear-obra-social/', ObraSocialCreate.as_view(), name='crear-obra-social'),
    path('administrador/menu-obras-sociales/eliminar-obra-social/<int:pk>/', ObraSocialDelete.as_view(), name='eliminar-obra-social'),
    path('administrador/ver-estadisticas/', EstadisticasView.as_view(), name='ver-estadisticas'),
    path('administrador/api/estadisticas/', ChartEstadisticas.as_view(), name='api-estadisticas'),
]