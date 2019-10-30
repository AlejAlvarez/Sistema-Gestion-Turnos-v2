from django.urls import path, include

from .views import exampleView

app_name = 'app_usuarios'

urlpatterns = [
    path('', exampleView, name='example'),
]