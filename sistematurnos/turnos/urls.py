# turnos/urls.py
from django.urls import path, include
from .views import HomePageView, UserView
from django.contrib.auth.views import LoginView

app_name = 'turnos'

urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
    path('profile/',UserView.as_view(),name="user-profile"),
]