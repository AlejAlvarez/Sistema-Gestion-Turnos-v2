from django.urls import path, include

from .views import exampleView, SignUpView, SignUpMedicoView

app_name = 'app_usuarios'

urlpatterns = [
    path('', exampleView, name='example'),
    path('registrar_usuario/', SignUpView.as_view(), name='registrar_usuario'),
    # path('loguearse/', )
    path('registrar_medico/', SignUpMedicoView.as_view(), name='registrar_medico'),
]