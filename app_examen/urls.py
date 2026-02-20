from django.urls import path
from . import views

app_name = 'app_examen'

urlpatterns = [
    path('<int:examen_id>/presentar/', views.ExamenView.presentar_examen, name='presentar_examen'),
    path('verificar-inactividad/', views.ExamenView.verificar_inactividad, name='verificar_inactividad'),
]
