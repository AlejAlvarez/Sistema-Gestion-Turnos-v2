from django.shortcuts import render
from django.http import HttpResponse

def exampleView(request):
    return HttpResponse("Pagina de turnos. Keré turnito'?")
