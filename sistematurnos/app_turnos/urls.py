from django.urls import path

from .views import *

app_name = 'app_turnos'

urlpatterns = [
    # path('', exampleView, name='example'),
    path('crear-turnos/', crear_turnos, name='crear-turnos'),
    path('buscar-turnos/', buscar_turnos, name='buscar-turnos'),
    path('reservar-turno/', reservar_turno, name='reservar-turno'),
    path('gestionar-turnos/', gestionar_turnos, name='gestionar-turnos'),
    path('seleccionar-turno/', seleccionar_turno_a_atender, name='seleccionar-turno-a-atender'),
    path('atender-turno/<int:turno_id>/', atender_turno, name='atender-turno'),
    path('mis-turnos/', ListarTurnos.as_view(), name='mis-turnos'),
]