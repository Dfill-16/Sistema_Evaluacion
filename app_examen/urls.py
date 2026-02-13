from django.urls import path
from . import views

app_name = 'app_examen'

urlpatterns = [
    # Rutas de Examen
    path('examenes/', views.ExamenView.lista_examenes, name='lista_examenes'),
    path('examenes/crear/', views.ExamenView.crear_examen, name='crear_examen'),
    path('examenes/<int:examen_id>/', views.ExamenView.detalle_examen, name='detalle_examen'),
    path('examenes/<int:examen_id>/editar/', views.ExamenView.editar_examen, name='editar_examen'),
    path('examenes/<int:examen_id>/eliminar/', views.ExamenView.eliminar_examen, name='eliminar_examen'),
    path('examenes/<int:examen_id>/presentar/', views.ExamenView.presentar_examen, name='presentar_examen'),
    path('examenes/verificar-inactividad/', views.ExamenView.verificar_inactividad, name='verificar_inactividad'),
    
    # Rutas de Pregunta
    path('preguntas/crear/<int:examen_id>/', views.PreguntaView.crear_pregunta, name='crear_pregunta'),
    path('preguntas/<int:pregunta_id>/editar/', views.PreguntaView.editar_pregunta, name='editar_pregunta'),
    path('preguntas/<int:pregunta_id>/eliminar/', views.PreguntaView.eliminar_pregunta, name='eliminar_pregunta'),
    
    # Rutas de Respuesta
    path('respuestas/crear/<int:pregunta_id>/', views.RespuestaView.crear_respuesta, name='crear_respuesta'),
    path('respuestas/<int:respuesta_id>/editar/', views.RespuestaView.editar_respuesta, name='editar_respuesta'),
    path('respuestas/<int:respuesta_id>/eliminar/', views.RespuestaView.eliminar_respuesta, name='eliminar_respuesta'),
]