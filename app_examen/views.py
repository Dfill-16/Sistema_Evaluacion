from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
from .models import Examen, Pregunta, Respuesta, ExamenCandidato, RespuestaCandidato
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
# Create your views here.

# Funciones auxiliares para verificar roles
def es_candidato(user):
    return user.is_authenticated and user.rol == 'candidato'


class ExamenView:

    def calcular_puntaje(examen_candidato):
        total_preguntas = examen_candidato.examen.preguntas.count()
        if total_preguntas == 0:
            return 0
        respuestas_candidato = examen_candidato.respuestas_dadas.all()
        correctas = sum(1 for respuesta in respuestas_candidato if respuesta.es_correcta)
        return round((correctas / total_preguntas) * 100, 2)
    @login_required
    @user_passes_test(es_candidato, login_url='/acceso-denegado/')
    def presentar_examen(request, examen_id):
        """Solo Candidatos - El examen se marca como completado al entrar"""
        examen = get_object_or_404(Examen, id=examen_id, activo=True)
        preguntas = examen.preguntas.prefetch_related('respuestas')
        
        total_preguntas = preguntas.count()
        if total_preguntas != 10:
            messages.error(request, 'Este examen no está disponible: debe tener exactamente 10 preguntas.')
            return redirect('candidato:dashboard')
        
        for pregunta in preguntas:
            if pregunta.respuestas.count() != 3:
                messages.error(request, 'Este examen no está disponible: cada pregunta debe tener exactamente 3 opciones.')
                return redirect('candidato:dashboard')
        
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
            for pregunta in preguntas:
                respuesta_id = request.POST.get(f'pregunta_{pregunta.id}')
                respuesta_obj = None
                es_correcta = False

                if respuesta_id:
                    respuesta_obj = get_object_or_404(Respuesta, id=respuesta_id, pregunta=pregunta)
                    es_correcta = respuesta_obj.es_correcta

                RespuestaCandidato.objects.update_or_create(
                    examen_candidato=examencandidato,
                    pregunta=pregunta,
                    defaults={
                        'respuesta_seleccionada': respuesta_obj,
                        'es_correcta': es_correcta
                    }
                )
             
            puntaje = ExamenView.calcular_puntaje(examen_candidato=examencandidato)
            examencandidato.puntaje = puntaje
            examencandidato.completado = True
            examencandidato.tiempo_empleado = timezone.now() - examencandidato.fecha_presentacion
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
    

