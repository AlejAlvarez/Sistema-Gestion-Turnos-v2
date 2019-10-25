# turnos/urls.py
from django.urls import path
from .views import HomePageView

app_name = 'turnos'

urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
]