"""sistematurnos URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # urls provided by auth: 
    # turnos/login/ [name='login']
    # turnos/logout/ [name='logout']
    # turnos/password_change/ [name='password_change']
    # turnos/password_change/done/ [name='password_change_done']
    # turnos/password_reset/ [name='password_reset']
    # turnos/password_reset/done/ [name='password_reset_done']
    # turnos/reset/<uidb64>/<token>/ [name='password_reset_confirm']
    # turnos/reset/done/ [name='password_reset_complete']
    path('turnos/',include('django.contrib.auth.urls')),
    path('turnos/',include('turnos.urls')),
]
