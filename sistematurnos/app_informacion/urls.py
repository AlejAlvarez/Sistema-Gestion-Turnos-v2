from django.urls import path, include

from .views import HomePageView

app_name = 'app_informacion'

urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
]