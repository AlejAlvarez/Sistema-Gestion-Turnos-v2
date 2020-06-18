# -*- coding: UTF-8 -*-
from __future__ import unicode_literals

from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils.text import slugify
from django.shortcuts import get_object_or_404
from django.http import Http404
from django.views import View
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.exceptions import PermissionDenied

from weasyprint import HTML

from ..models import Turno

class ObtenerTurnoPDF(View):

    def get(self, request, *args, **kwargs):
        turno = get_object_or_404(Turno,pk=kwargs['turno_pk'])
        user = request.user
        if user.is_authenticated:
            is_owner_turno = user.has_perm('turnos_app.es_paciente') and (request.user.pk == turno.paciente.pk)
            if (user.has_perm('turnos_app.es_recepcionista')) or (is_owner_turno):
                response = HttpResponse(content_type='application/pdf')
                turno_filename = "%s_%d" % (turno.paciente,turno.pk)
                response['Content-Disposition'] = 'filename=%s.pdf' % turno_filename
                context = {
                    'turno': turno
                }
                html = render_to_string('turno_template.html',context)
                HTML(string=html, base_url=request.build_absolute_uri()).write_pdf(response)
                return response
            else:
                raise PermissionDenied
        else:
            raise PermissionDenied

def obtener_turno_pdf(request,turno_pk):
    turno = get_object_or_404(Turno,pk=turno_pk)
    response = HttpResponse(content_type='application/pdf')
    turno_filename = "%s_%d" % (turno.paciente,turno.pk)
    response['Content-Disposition'] = 'filename=%s.pdf' % turno_filename
    context = {
        'turno': turno
    }
    html = render_to_string('turno_template.html',context)
    HTML(string=html, base_url=request.build_absolute_uri()).write_pdf(response)
    return response