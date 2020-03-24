from django.urls import path,include, re_path
from django.contrib.auth import views as auth_views

from .views.page_views import *
from .views.views_usuario import *
from .views.views_paciente import *
from .views.views_recepcionista import *
from .views.views_medico import *
from .views.views_administrador import *
from .views.ajax_views import *

paciente_patterns = [

    path('login/',LoginPacienteView.as_view(),name='login-paciente'),
    path('logout/',auth_views.LogoutView.as_view(template_name='paciente/logout.html'),name='logout-paciente'),
    path('index/',index_paciente,name='index-paciente'),
    path('buscar-turnos/',buscar_turnos,name='hacer-reserva'),
    path('confirmar-reserva/<int:pk>/',reservar_turno_paciente,name='confirmar-reserva'),
    path('ver-turno/<int:pk>/',VerTurno.as_view(),name='ver-turno'),
    path('cancelar-turno/<int:pk>',CancelarTurnoView.as_view(),name='cancelar-turno'),
    path('cancelar-turno/<int:pk>/cancelado/',TurnoCanceladoView.as_view(),name='turno-cancelado'),
    path('historial/',HistorialPacienteView.as_view(),name='ver-historial'),
    path('mis-turnos/',ListarTurnos.as_view(),name='mis-turnos'),
    path('buscar-turnos/',buscar_turnos,name='buscar-turnos'),
    path('ajax/filtrar-medicos/',BuscarMedicosAjax.as_view(),name='filtrar-medicos-ajax'),
    path('ajax/buscar-turnos/',BuscarTurnosAjax.as_view(),name='buscar-turnos-ajax'),
    #path('paciente/editar/<int:pk>/',editar_paciente, name='editar-paciente'),

]

recepcionista_patterns = [

    path('login/',LoginRecepcionistaView.as_view(),name='login-recepcionista'),
    path('logout/',auth_views.LogoutView.as_view(template_name='recepcionista/logout.html'),name='logout-recepcionista'),
    path('index/',index_recepcionista,name='index-recepcionista'),
    path('gestionar-turnos/<int:pk>',GestionarTurnosView.as_view(),name='gestionar-turnos'),
    path('atender-usuario/',AtenderUsuarioView.as_view(),name='atender-usuario'),
    path('registrar-paciente/',SignUpPacienteView.as_view(),name='registrar-paciente'),
    path('reservar-turno/<int:pk>/',ReservarTurnoView.as_view(),name='reservar-turno'),
    path('imprimir-reserva/<int:pacientepk>/<int:pk>/',ImprimirReservaView.as_view(),name='imprimir-reserva'),
    path('ajax/buscar-turnos',ConsultarTurnosEspecialidadAjax.as_view(),name='consultar-turnos-especialidad-ajax'),
    path('ajax/obtener-paciente',ObtenerPacienteAjax.as_view(),name='obtener-paciente-ajax'),
    path('ajax/realizar-reserva/',RealizarReservaAjax.as_view(),name='realizar-reserva-ajax'),
    path('ajax/confirmar-reserva/',ConfirmarReservaAjax.as_view(),name='confirmar-reserva-ajax'),
]

#medico_patterns = [
    #path('medico/index',index_medico,'index-medico'),
    #path('medico/ver-turnos',ver_turnos,'ver-turnos'),
    #path('medico/atender-turno/<int:pk>',atender_turno,'atender-turno'),
    #path('medico/actualizar-horarios',actualizar_horarios,'actualizar-horarios'),
    #path('medico/crear-turnos')
#]
administrador_patterns = [

    path('login/', LoginAdministradorView.as_view(), name='login-administrador'),
    path('logout/',logout_usuario,name='logout-administrador'),
    path('', index_administrador,name='index-administrador'),
    path('menu-recepcionistas/', RecepcionistaListView.as_view(), name='menu-recepcionistas'),
    path('registrar-recepcionista/', SignUpRecepcionistaView.as_view(), name='registrar-recepcionista'),
    path('editar-recepcionista/<int:pk>/', editar_informacion_recepcionista, name='editar-recepcionista'),
    path('ver-recepcionista/<int:pk>/', DetailsRecepcionista.as_view(), name='ver-recepcionista'),
    path('eliminar-recepcionista/<int:pk>/', EliminarRecepcionistaView.as_view(), name='eliminar-recepcionista'),
    path('menu-medicos/', MedicoListView.as_view(), name='menu-medicos'),
    path('registrar-medico/', SignUpMedicoView.as_view(), name='registrar-medico'),
    path('editar-medico/<int:pk>/', editar_informacion_medico, name='editar-medico'),
    path('ver-medico/<int:pk>/', DetailsMedico.as_view(), name='ver-medico'),
    path('eliminar-medico/<int:pk>/', EliminarMedicoView.as_view(), name='eliminar-medico'),
    path('menu-administradores/', AdministradorListView.as_view(), name='menu-administradores'),
    path('registrar-administrador/', SignUpAdministradorView.as_view(), name='registrar-administrador'),
    path('editar-administrador/<int:pk>/', editar_informacion_administrador, name='editar-administrador'),
    path('ver-administrador/<int:pk>/', DetailsAdministrador.as_view(), name='ver-administrador'),
    path('eliminar-administrador/<int:pk>/', EliminarAdministradorView.as_view(), name='eliminar-administrador'),
    path('menu-pacientes/', PacienteListView.as_view(), name='menu-pacientes'),
    path('menu-pacientes/eliminar-paciente/<int:pk>/', EliminarPacienteView.as_view(), name='eliminar-paciente'),
    path('menu-especialidades/', EspecialidadListView.as_view(), name='menu-especialidades'),
    path('crear-especialidad/', EspecialidadCreate.as_view(), name='crear-especialidad'),
    path('menu-especialidades/eliminar-especialidad/<int:pk>/', EspecialidadDelete.as_view(), name='eliminar-especialidad'),
    path('menu-obras-sociales/', ObraSocialListView.as_view(), name='menu-obras-sociales'),
    path('crear-obra-social/', ObraSocialCreate.as_view(), name='crear-obra-social'),
    path('menu-obras-sociales/eliminar-obra-social/<int:pk>/', ObraSocialDelete.as_view(), name='eliminar-obra-social'),
    path('ver-estadisticas/', EstadisticasView.as_view(), name='ver-estadisticas'),
    path('api/estadisticas/', ChartEstadisticas.as_view(), name='api-estadisticas'),
]
urlpatterns = [

    # general

    path('',home,name='home'),
    path('paciente/',include(paciente_patterns)),
    path('recepcionista/',include(recepcionista_patterns)),
    path('administrador/',include(administrador_patterns)),

]