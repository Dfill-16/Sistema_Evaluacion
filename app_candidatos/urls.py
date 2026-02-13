from django.urls import path
from . import views

app_name = 'app_candidatos'

urlpatterns = [
    # Gestión de Candidatos (Solo Administradores)
    path('registrar/', views.registrar_candidato, name='registrar_candidato'),
    path('lista/', views.lista_candidatos, name='lista_candidatos'),
    path('<int:candidato_id>/', views.detalle_candidato, name='detalle_candidato'),
    path('<int:candidato_id>/editar/', views.editar_candidato, name='editar_candidato'),
    path('<int:candidato_id>/eliminar/', views.eliminar_candidato, name='eliminar_candidato'),
    
    # Tabla de Posiciones (Solo Administradores)
    path('tabla-posiciones/', views.tabla_posiciones, name='tabla_posiciones'),
]
