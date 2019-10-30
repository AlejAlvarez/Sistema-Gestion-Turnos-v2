from django.urls import path

from .views import exampleView

app_name = 'app_turnos'

urlpatterns = [
    path('', exampleView, name='example'),
]