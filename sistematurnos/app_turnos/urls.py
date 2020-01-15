from django.urls import path

from .views import *

app_name = 'app_turnos'

urlpatterns = [
    # path('', exampleView, name='example'),
    path('crear-turnos/', crear_turnos, name='crear-turnos'),
    path('buscar-turnos/', buscar_turnos, name='buscar-turnos'),
    path('reservar-turno/', reservar_turno, name='reservar-turno'),
    path('reservar-turnos/',reservar_turnos, name='reservar-turnos'),
    path('completar-reserva/<int:turno_id>',completar_reserva, name='completar-reserva'),
    path('gestionar-turnos/', gestionar_turnos, name='gestionar-turnos'),
    path('seleccionar-turno/', seleccionar_turno_a_atender, name='seleccionar-turno-a-atender'),
    path('atender-turno/<int:turno_id>/', atender_turno, name='atender-turno'),
    path('mis-turnos/', ListarTurnos.as_view(), name='mis-turnos'),
    path('ver-turno/<int:pk>/', VerTurno.as_view(), name='ver-turno'),
    path('cancelar-turno/<int:pk>/', cancelar_turno, name='cancelar-turno'),
    path('historial/', ver_historial, name='ver-historial'),
    path('reservar-turnos/ajax/filtrar-especialidad/', ObtenerTurnosAjax.as_view(),name='get-turnos-ajax')
]