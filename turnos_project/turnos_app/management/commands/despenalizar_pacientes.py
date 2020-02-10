from django.core.management.base import BaseCommand, CommandError
from turnos_app.models import Paciente
from datetime import datetime, timedelta, date


class Command(BaseCommand):
    help = 'Despenaliza aquellos pacientes que ya cumplieron con el tiempo.'

    def handle(self, *args, **options):

        manana = datetime.today() + timedelta(days=1)
        hoy = datetime.today()

        pacientes = Paciente.objects.filter(penalizado=True, fecha_despenalizacion__range=[hoy, manana])

        despenalizados = []

        # Despenaliza a los pacientes cuya fecha sea la de hoy, sin importar la hora.

        for paciente in pacientes:
            paciente.penalizado = False
            paciente.fecha_despenalizacion = None
            paciente.save()
            despenalizados.append(paciente)


        if despenalizados:
            self.stdout.write(self.style.SUCCESS('Se han despenalizado los siguientes pacientes: '))

            for paciente in despenalizados:
                self.stdout.write(self.style.SUCCESS(paciente))
         else:
            self.stdout.write(self.style.SUCCESS('No se ha despenalizado ningún paciente.'))

