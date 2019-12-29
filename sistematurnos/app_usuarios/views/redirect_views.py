from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.http import HttpResponse
from django.urls import reverse_lazy


# de acuerdo al permiso y tipo de usuario, se lo va a redirigir a su correspondiente pÃ¡gina de perfil
def redirect_logged_user(user):
    if(user.is_authenticated):
        name = user.first_name
        if (user.has_perm('is_superuser')):
            return redirect('/admin')
        elif (user.has_perm("app_usuarios.es_paciente")):
            return redirect(reverse_lazy('app_usuarios:perfil-paciente'),request=request)    
        else:    
            return HttpResponse("Hola" + name + "!") 

def log_user(request):
    if request.method == 'POST':   
        username = request.POST['username']
        password = request.POST['password'] 
        user = authenticate(request,username=username,password=password)
        if user is not None:
            login(request,user)
            # de acuerdo al permiso y tipo de usuario, se lo va a redirigir a su correspondiente página de perfil
            name = user.first_name
            if (user.has_perm('is_superuser')):
                return redirect('/admin')
            elif (user.has_perm("app_usuarios.es_paciente")):
                return redirect(reverse_lazy('app_usuarios:perfil-paciente'),request=request)  
            elif (user.has_perm('app_usuarios.es_recepcionista')):
                return redirect(reverse_lazy('app_usuarios:index-recepcionista'),request=request)
            else:    
                return HttpResponse("Hola" + name + "!") 
        else:
            return redirect(reverse_lazy('login'))
    # quiere decir que es un método GET          
    else:
        if request.user.is_authenticated:
            name = request.user.first_name
            if (request.user.has_perm('is_superuser')):
                return redirect('/admin')
            elif (request.user.has_perm("app_usuarios.es_paciente")):
                return redirect(reverse_lazy('app_usuarios:perfil-paciente'),request=request)    
            else:    
                return HttpResponse("Hola" + name + "!") 
        else:
            return redirect(reverse_lazy('login'))
