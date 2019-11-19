from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.urls import reverse_lazy


# de acuerdo al permiso y tipo de usuario, se lo va a redirigir a su correspondiente pÃ¡gina de perfil
def redirect_logged_user(request):
    if(request.user.is_authenticated):
        name = request.user.first_name
        if (request.user.has_perm("app_usuarios.is_patient")):
            return redirect(reverse_lazy('app_usuarios:perfil-paciente'),request=request)
        else:
            return HttpResponse("Hola" + name + "!") 
    else:
        return redirect(reverse_lazy('login'))