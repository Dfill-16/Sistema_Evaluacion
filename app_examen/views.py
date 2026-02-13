from django.shortcuts import render, get_object_or_404, redirect
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
from .models import Examen, Pregunta, Respuesta, ExamenCandidato, RespuestaCandidato
from django.contrib.auth.decorators import login_required, user_passes_test
# Create your views here.

# Funciones auxiliares para verificar roles
def es_administrador(user):
    return user.is_authenticated and (user.rol == 'admin' or user.is_superuser)

def es_superusuario(user):
    return user.is_authenticated and user.is_superuser

def es_candidato(user):
    return user.is_authenticated and user.rol == 'candidato'


class ExamenView:

    @login_required
    @user_passes_test(es_administrador, login_url='/acceso-denegado/')
    def lista_examenes(request):
        """Solo Administradores"""
        examenes = Examen.objects.filter(activo=True)
        return render(request, 'app_examen/lista_examenes.html', {'examenes': examenes})

    @login_required
    @user_passes_test(es_administrador, login_url='/acceso-denegado/')
    def crear_examen(request):
        """Solo Administradores"""
        if request.method == 'POST':
            nombre = request.POST.get('nombre')
            descripcion = request.POST.get('descripcion')
            examen = Examen.objects.create(nombre=nombre, descripcion=descripcion)
            return render(request, 'app_examen/detalle_examen.html', {'examen': examen})
        return render(request, 'app_examen/crear_examen.html')
    
    @login_required
    @user_passes_test(es_administrador, login_url='/acceso-denegado/')
    def editar_examen(request, examen_id):
        """Solo Administradores"""
        examen = get_object_or_404(Examen, id=examen_id)
        if request.method == 'POST':
            examen.nombre = request.POST.get('nombre')
            examen.descripcion = request.POST.get('descripcion')
            examen.save()

    @login_required
    @user_passes_test(es_administrador, login_url='/acceso-denegado/')
    def detalle_examen(request, examen_id):
        """Solo Administradores"""
        examen = get_object_or_404(Examen, id=examen_id)
        preguntas = examen.preguntas.all()
        return render(request, 'app_examen/detalle_examen.html', {'examen': examen, 'preguntas': preguntas})

    def calcular_puntaje(examen_candidato):
        puntaje = 0
        respuestas_candidato = examen_candidato.respuestas.all()
        for respuesta in respuestas_candidato:
            if respuesta.es_correcta:
                puntaje += 1
        return puntaje
    
    @login_required
    @user_passes_test(es_administrador, login_url='/acceso-denegado/')
    def eliminar_examen(request, examen_id):
        """Solo Administradores"""
        examen = get_object_or_404(Examen, id=examen_id)
        examen.activo = False
        examen.save()
        return render(request, 'app_examen/lista_examenes.html', {'examenes': Examen.objects.filter(activo=True)})

    @login_required
    @user_passes_test(es_candidato, login_url='/acceso-denegado/')
    def presentar_examen(request, examen_id):
        """Solo Candidatos - El examen se marca como completado al entrar"""
        examen = get_object_or_404(Examen, id=examen_id, activo=True)
        preguntas = examen.preguntas.all()
        
        # Validar que el candidato no haya completado el examen anteriormente
        examen_previo = ExamenCandidato.objects.filter(
            candidato=request.user, 
            examen=examen, 
            completado=True
        ).first()
        
        if examen_previo:
            return render(request, 'app_examen/resultado_examen.html', {
                'examen': examen, 
                'puntaje': examen_previo.puntaje, 
                'mensaje': f'Ya has presentado este examen anteriormente. Tu puntaje fue: {examen_previo.puntaje}'
            })
        
        # Buscar si existe un registro previo no completado
        examencandidato = ExamenCandidato.objects.filter(
            candidato=request.user, 
            examen=examen
        ).first()
        
        if examencandidato:
            # Si ya existe marcar como completado y mostrar resultado
            if not examencandidato.completado:
                puntaje = ExamenView.calcular_puntaje(examen_candidato=examencandidato)
                examencandidato.puntaje = puntaje
                examencandidato.completado = True
                examencandidato.save()
                
                return render(request, 'app_examen/resultado_examen.html', {
                    'examen': examen, 
                    'puntaje': puntaje,
                    'mensaje': 'El examen fue cerrado. Solo tienes una oportunidad para presentarlo.'
                })
        else:
            # Primera vez que entra - crear registro y marcar fecha de inicio
            examencandidato = ExamenCandidato.objects.create(
                candidato=request.user, 
                examen=examen,
                completado=False
            )
            # Guardar el ID del examen en sesión para monitorear inactividad
            request.session['examen_iniciado_id'] = examencandidato.id
            request.session['examen_inicio_tiempo'] = timezone.now().isoformat()
        
        if request.method == 'POST':
            respuestas = request.POST.getlist('respuestas')
             
            puntaje = ExamenView.calcular_puntaje(examen_candidato=examencandidato)
            examencandidato.puntaje = puntaje
            examencandidato.completado = True
            examencandidato.save()
            
            # Limpiar sesión
            if 'examen_iniciado_id' in request.session:
                del request.session['examen_iniciado_id']
            if 'examen_inicio_tiempo' in request.session:
                del request.session['examen_inicio_tiempo']
            
            return render(request, 'app_examen/resultado_examen.html', {
                'examen': examen, 
                'puntaje': puntaje
            })

        return render(request, 'app_examen/presentar_examen.html', {
            'examen': examen, 
            'preguntas': preguntas,
            'tiempo_limite_inactividad': 120  # 2 minutos en segundos
        })
    
    @login_required
    @user_passes_test(es_candidato, login_url='/acceso-denegado/')
    def verificar_inactividad(request):
        """Endpoint para verificar inactividad en la pestaña y marcar examen como completado"""
        if request.method == 'POST':
            examen_iniciado_id = request.session.get('examen_iniciado_id')
            
            if not examen_iniciado_id:
                return JsonResponse({'status': 'error', 'message': 'No hay examen activo'})
            
            try:
                examencandidato = ExamenCandidato.objects.get(
                    id=examen_iniciado_id,
                    candidato=request.user,
                    completado=False
                )
                
                # Marcar como completado por inactividad
                puntaje = ExamenView.calcular_puntaje(examen_candidato=examencandidato)
                examencandidato.puntaje = puntaje
                examencandidato.completado = True
                examencandidato.save()
                
                # Limpiar sesión
                if 'examen_iniciado_id' in request.session:
                    del request.session['examen_iniciado_id']
                if 'examen_inicio_tiempo' in request.session:
                    del request.session['examen_inicio_tiempo']
                
                return JsonResponse({
                    'status': 'completado',
                    'message': 'Examen completado por inactividad',
                    'puntaje': float(puntaje)
                })
                
            except ExamenCandidato.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'Examen no encontrado'})
        
        return JsonResponse({'status': 'error', 'message': 'Método no permitido'})
    
    
class PreguntaView:

    @login_required
    @user_passes_test(es_superusuario, login_url='/acceso-denegado/')
    def crear_pregunta(request, examen_id):
        """Solo Superusuarios - Gestión del banco de preguntas"""
        examen = get_object_or_404(Examen, id=examen_id)
        preguntas_existentes = examen.preguntas.count()
        if preguntas_existentes >= 10:
            return render(request, 'app_examen/crear_pregunta.html', {'examen': examen, 'error': 'Un examen no puede tener más de 10 preguntas.'})
        
        if request.method == 'POST':
            contenido = request.POST.get('contenido')
            orden = request.POST.get('orden', 0)
            imagen = request.FILES.get('imagen')
            pregunta = Pregunta.objects.create(examen=examen, contenido=contenido, orden=orden, imagen=imagen)
            return render(request, 'app_examen/detalle_examen.html', {'examen': examen, 'preguntas': examen.preguntas.all()})
        return render(request, 'app_examen/crear_pregunta.html', {'examen': examen})
    
    @login_required
    @user_passes_test(es_superusuario, login_url='/acceso-denegado/')
    def editar_pregunta(request, pregunta_id):
        """Solo Superusuarios - Gestión del banco de preguntas"""
        pregunta = get_object_or_404(Pregunta, id=pregunta_id)
        if request.method == 'POST':
            pregunta.contenido = request.POST.get('contenido')
            pregunta.orden = request.POST.get('orden', 0)
            imagen = request.FILES.get('imagen')
            if imagen:
                pregunta.imagen = imagen
            pregunta.save()
            return render(request, 'app_examen/detalle_examen.html', {'examen': pregunta.examen, 'preguntas': pregunta.examen.preguntas.all()})
        return render(request, 'app_examen/editar_pregunta.html', {'pregunta': pregunta})
    
    @login_required
    @user_passes_test(es_superusuario, login_url='/acceso-denegado/')
    def eliminar_pregunta(request, pregunta_id):
        """Solo Superusuarios - Gestión del banco de preguntas"""
        pregunta = get_object_or_404(Pregunta, id=pregunta_id)
        examen = pregunta.examen
        pregunta.delete()
        return render(request, 'app_examen/detalle_examen.html', {'examen': examen, 'preguntas': examen.preguntas.all()})
    
class RespuestaView:

    @login_required
    @user_passes_test(es_superusuario, login_url='/acceso-denegado/')
    def crear_respuesta(request, pregunta_id):
        """Solo Superusuarios - Gestión del banco de preguntas"""
        pregunta = get_object_or_404(Pregunta, id=pregunta_id)
        respuestas_existentes = pregunta.respuestas.all()
        if respuestas_existentes.count() >= 3:
            return render(request, 'app_examen/crear_respuesta.html', {'pregunta': pregunta, 'error': 'Una pregunta no puede tener más de 3 respuestas.'})
        if request.method == 'POST':
            contenido = request.POST.get('contenido')
            
            #validar que solo una respuesta sea correcta
            if request.POST.get('es_correcta') == 'on' and respuestas_existentes.filter(es_correcta=True).exists():
                return render(request, 'app_examen/crear_respuesta.html', {'pregunta': pregunta, 'error': 'Ya existe una respuesta correcta para esta pregunta.'})
            
            es_correcta = request.POST.get('es_correcta') == 'on'
            respuesta = Respuesta.objects.create(pregunta=pregunta, contenido=contenido, es_correcta=es_correcta)
            return render(request, 'app_examen/detalle_examen.html', {'examen': pregunta.examen, 'preguntas': pregunta.examen.preguntas.all()})
        return render(request, 'app_examen/crear_respuesta.html', {'pregunta': pregunta})
    
    @login_required
    @user_passes_test(es_superusuario, login_url='/acceso-denegado/')
    def editar_respuesta(request, respuesta_id):
        """Solo Superusuarios - Gestión del banco de preguntas"""
        respuesta = get_object_or_404(Respuesta, id=respuesta_id)
        if request.method == 'POST':
            respuesta.contenido = request.POST.get('contenido')
            respuesta.es_correcta = request.POST.get('es_correcta') == 'on'
            respuesta.save()
            return render(request, 'app_examen/detalle_examen.html', {'examen': respuesta.pregunta.examen, 'preguntas': respuesta.pregunta.examen.preguntas.all()})
        return render(request, 'app_examen/editar_respuesta.html', {'respuesta': respuesta})
    
    @login_required
    @user_passes_test(es_superusuario, login_url='/acceso-denegado/')
    def eliminar_respuesta(request, respuesta_id):
        """Solo Superusuarios - Gestión del banco de preguntas"""
        respuesta = get_object_or_404(Respuesta, id=respuesta_id)
        pregunta = respuesta.pregunta
        respuesta.delete()
        return render(request, 'app_examen/detalle_examen.html', {'examen': pregunta.examen, 'preguntas': pregunta.examen.preguntas.all()})

