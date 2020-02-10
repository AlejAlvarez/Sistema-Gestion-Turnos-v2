from django.core.management.base import BaseCommand, CommandError
from turnos_app.models import Paciente, Turno, TurnoCancelado
from datetime import datetime, timedelta, date

class Command(BaseCommand):
    help = 'Penaliza aquellos pacientes que no confirmaron su turno en el día de la fecha'

    def handle(self, *args, **options):

        ayer = datetime.today() - timedelta(days=1)
        hoy = datetime.today()

        turnos = Turno.objects.filter(fecha__range=[ayer, hoy], estado=2)

        penalizados = []

        # Por cada turno no confirmado ayer, se penaliza al paciente involucrado.

        for turno in turnos:

            turno.estado = 5
            turno.save()

            turno_cancelado = TurnoCancelado.objects.create(turno=turno, fecha_cancelado=datetime.today())
            turno_cancelado.save()

            paciente = turno.paciente
            paciente.penalizado = True
            paciente.fecha_despenalizacion = date.today() + timedelta(days=7)
            paciente.save()
            penalizados.append(paciente)

        if penalizados:
            self.stdout.write(self.style.SUCCESS('Se han penalizado los siguientes pacientes: '))

            for paciente in penalizados:
                self.stdout.write(self.style.SUCCESS(paciente))
         else:
            self.stdout.write(self.style.SUCCESS('No se ha penalizado ningún paciente.'))
