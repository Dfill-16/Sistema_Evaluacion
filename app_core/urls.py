from django.urls import path
from . import views

app_name = 'app_core'

urlpatterns = [
    # Gestión de Administradores (Solo Superusuarios)
    path('administradores/registrar/', views.registrar_administrador, name='registrar_administrador'),
    path('administradores/lista/', views.lista_administradores, name='lista_administradores'),
    path('administradores/<int:admin_id>/', views.detalle_administrador, name='detalle_administrador'),
    path('administradores/<int:admin_id>/editar/', views.editar_administrador, name='editar_administrador'),
    path('administradores/<int:admin_id>/eliminar/', views.eliminar_administrador, name='eliminar_administrador'),
    path('administradores/<int:admin_id>/activar/', views.activar_administrador, name='activar_administrador'),
]
