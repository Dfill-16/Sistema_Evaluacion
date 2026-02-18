from django.urls import path
from . import views

app_name = 'app_candidatos'

urlpatterns = [
    # Entrada por defecto
    path('', views.lista_candidatos, name='home_candidatos'),
    
    # Gestión de Candidatos (Solo Administradores)
    path('registrar/', views.registrar_candidato, name='registrar_candidato'),
    path('lista/', views.lista_candidatos, name='lista_candidatos'),
    path('<int:candidato_id>/', views.detalle_candidato, name='detalle_candidato'),
    path('<int:candidato_id>/editar/', views.editar_candidato, name='editar_candidato'),
    path('<int:candidato_id>/eliminar/', views.eliminar_candidato, name='eliminar_candidato'),
    
    # Tabla de Posiciones (Solo Administradores)
    path('tabla-posiciones/', views.tabla_posiciones, name='tabla_posiciones'),
    
    # Dashboard Candidato + perfil
    path('dashboard/', views.dashboard_candidato, name='dashboard_candidato'),
    path('dashboard/inicio/', views.dashboard_candidato, name='dashboard'),
    path('mi-perfil/', views.mi_perfil, name='mi_perfil'),
]
