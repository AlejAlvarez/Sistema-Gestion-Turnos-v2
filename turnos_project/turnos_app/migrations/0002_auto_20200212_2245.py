# Generated by Django 2.2 on 2020-02-12 22:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('turnos_app', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='customuser',
            options={'permissions': (('es_recepcionista', 'Usuario tiene rol de recepcionista'), ('es_administrador', 'Usuario tiene rol de administrador'), ('es_paciente', 'Usuario tiene rol de paciente'), ('es_medico', 'Usuario tiene rol de medico'))},
        ),
        migrations.AlterModelOptions(
            name='medico',
            options={},
        ),
        migrations.AlterModelOptions(
            name='paciente',
            options={},
        ),
    ]
