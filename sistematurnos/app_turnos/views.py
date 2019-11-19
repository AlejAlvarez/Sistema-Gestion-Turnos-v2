from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import ListView

from datetime import timedelta, datetime, date

from .models import *
from app_usuarios.models import Medico, CustomUser
from .forms import TurnoForm

def exampleView(request):
    return HttpResponse("Pagina de turnos. Keré turnito'?")

# Funcion lambda utilizada para calcular los días de los turnos
onDay = lambda dt, day: dt + timedelta(days=(day - dt.weekday())%7)

def crear_turnos(request):
    if request.user.is_authenticated:
        usuario = CustomUser.objects.get(pk=request.user.id)
        if usuario.user_type == 3:
            if request.method == 'POST':
                form = TurnoForm(request.POST)
                if form.is_valid():
                    dias        = form.cleaned_data.get('dias_atencion')
                    hora_inicio = form.cleaned_data.get('hora_inicio')
                    hora_fin    = form.cleaned_data.get('hora_fin')
                    duracion    = form.cleaned_data.get('duracion_turno')
                    sobreturnos = form.cleaned_data.get('sobreturnos')
                    medico      = Medico.objects.get(user=usuario)

                    # Esto corrobora que no se estén superponiendo horarios laborales ya creados
                    for dia in dias:
                        try:
                            dia_laboral = DiaLaboral.objects.get(medico=medico, dia=dia)
                            print(dia_laboral)
                            horarios_laborales_existentes = HorarioLaboral.objects.filter(dia_laboral=dia_laboral)
                            if horarios_laborales_existentes:
                                for horario in horarios_laborales_existentes:
                                    if(hora_inicio >= horario.hora_inicio and hora_inicio < horario.hora_fin) or (hora_fin > horario.hora_inicio and hora_fin <= horario.hora_fin):
                                        return HttpResponse("Error, se están superponiendo horarios.")
                        except DiaLaboral.DoesNotExist:
                            print("Dia ", dia, " no se encuentra creado actualmente.")
                    
                    # Creamos los turnos en cada dia, con los distintos horarios posibles.
                    for dia in dias:
                        fecha_laboral = onDay(date.today(), int(dia))
                        dia_laboral = DiaLaboral.objects.get_or_create(medico=medico, dia=dia)[0]
                        print(dia_laboral)
                        horario_laboral = HorarioLaboral.objects.create(dia_laboral=dia_laboral, hora_inicio=hora_inicio, hora_fin=hora_fin, sobreturnos=sobreturnos)
                        mes_actual = date.today().month
                        while fecha_laboral.month == mes_actual:
                            hora_turno = datetime.combine(fecha_laboral, hora_inicio)
                            while hora_turno.time() <= hora_fin:
                                turno = Turno()
                                turno.medico = medico
                                turno.estado = 1 # Estado 1 = 'disponible'
                                fecha_atencion = datetime.combine(fecha_laboral, hora_turno.time())
                                print("Dia laboral: ", fecha_laboral)
                                print("Fecha de atencion: ", fecha_atencion)
                                turno.fecha  = fecha_atencion
                                turno.save()
                                hora_turno = hora_turno + timedelta(minutes=duracion)
                            print("Salió del loop de hora_turno")
                            fecha_laboral = onDay(fecha_laboral + timedelta(days=7), 1)
                        print("Termino de cargar turnos para el mes")
            else:
                form = TurnoForm()
        else:
            return HttpResponse("Debe ser médico para realizar esta acción.")
    else:
        return HttpResponse("Debe estar logueado para acceder a esta función")
        
    return render(request, 'turnos/crear_turnos.html', {'form': form})


class ListarTurnos(ListView):
    model = Turno
    template_name = "turnos/lista_turnos.html"
    object_context_name = "lista_turnos"
    queryset = Turno.objects.all()
    paginate_by = 20





