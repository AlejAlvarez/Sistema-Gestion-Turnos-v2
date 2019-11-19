from django.urls import path

from .views import *

app_name = 'app_turnos'

urlpatterns = [
    path('', exampleView, name='example'),
    path('crear-turnos/', crear_turnos, name='crear_turnos'),
    path('ver-turnos/', ListarTurnos.as_view(), name='ver-turnos'),
]