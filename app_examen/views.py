from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
from django.db import transaction
from .models import Examen, Pregunta, Respuesta, ExamenCandidato, RespuestaCandidato
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
# Create your views here.

# Funciones auxiliares para verificar roles
def es_candidato(user):
    return user.is_authenticated and user.rol == 'candidato'


class ExamenView:

    @login_required
    @user_passes_test(es_administrador, login_url='/acceso-denegado/')
    def lista_examenes(request):
        """Solo Administradores"""
        examenes = Examen.objects.filter(activo=True).prefetch_related('preguntas', 'examenes_candidatos')
        total_preguntas = sum(examen.preguntas.count() for examen in examenes)
        total_intentos = sum(examen.examenes_candidatos.count() for examen in examenes)
        return render(request, 'app_examen/lista_examenes.html', {
            'examenes': examenes,
            'total_preguntas': total_preguntas,
            'total_intentos': total_intentos,
        })

    @login_required
    @user_passes_test(es_administrador, login_url='/acceso-denegado/')
    def crear_examen(request):
        """Solo Administradores"""
        if request.method == 'POST':
            nombre = request.POST.get('nombre')
            descripcion = request.POST.get('descripcion')
            examen = Examen.objects.create(nombre=nombre, descripcion=descripcion)
            messages.success(request, f'Examen "{examen.nombre}" creado. Ahora agrega las preguntas.')
            return redirect('app_examen:crear_pregunta', examen_id=examen.id)
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
            return redirect('app_examen:detalle_examen', examen_id=examen.id)
        return render(request, 'app_examen/editar_examen.html', {'examen': examen})

    @login_required
    @user_passes_test(es_administrador, login_url='/acceso-denegado/')
    def detalle_examen(request, examen_id):
        """Solo Administradores"""
        examen = get_object_or_404(Examen, id=examen_id)
        preguntas = examen.preguntas.all()
        return render(request, 'app_examen/detalle_examen.html', {'examen': examen, 'preguntas': preguntas})

    def calcular_puntaje(examen_candidato):
        total_preguntas = examen_candidato.examen.preguntas.count()
        if total_preguntas == 0:
            return 0
        respuestas_candidato = examen_candidato.respuestas_dadas.all()
        correctas = sum(1 for respuesta in respuestas_candidato if respuesta.es_correcta)
        return round((correctas / total_preguntas) * 100, 2)
    
    @login_required
    @user_passes_test(es_superusuario, login_url='/acceso-denegado/')
    def eliminar_examen(request, examen_id):
        """Solo Administradores"""
        examen = get_object_or_404(Examen, id=examen_id)
        examen.activo = False
        examen.save()
        return redirect('app_examen:lista_examenes')

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
            # Si existe y no está completado: solo cerrar en GET (re-entrada sin haber enviado)
            if not examencandidato.completado and request.method == 'GET':
                puntaje = ExamenView.calcular_puntaje(examen_candidato=examencandidato)
                examencandidato.puntaje = puntaje
                examencandidato.completado = True
                examencandidato.save()
                
                return render(request, 'app_examen/resultado_examen.html', {
                    'examen': examen, 
                    'puntaje': puntaje,
                    'mensaje': 'El examen fue cerrado. Solo tienes una oportunidad para presentarlo.'
                })
            # Si es POST con examen no completado, continúa al bloque de envío
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
    
    
class PreguntaView:

    @login_required
    @user_passes_test(es_superusuario, login_url='/acceso-denegado/')
    def crear_pregunta(request, examen_id):
        """Solo Superusuarios - Gestión del banco de preguntas"""
        examen = get_object_or_404(Examen, id=examen_id)
        preguntas_existentes = examen.preguntas.count()
        if preguntas_existentes >= 10:
            return render(request, 'app_examen/crear_pregunta.html', {
                'examen': examen,
                'error': 'Un examen no puede tener más de 10 preguntas.',
            })
        
        if request.method == 'POST':
            contenido = request.POST.get('contenido', '').strip()
            imagen = request.FILES.get('imagen')
            respuesta_1 = request.POST.get('respuesta_1', '').strip()
            respuesta_2 = request.POST.get('respuesta_2', '').strip()
            respuesta_3 = request.POST.get('respuesta_3', '').strip()
            correcta = request.POST.get('correcta', '')

            errores = []
            if not contenido:
                errores.append('El contenido de la pregunta es obligatorio.')
            if not respuesta_1 or not respuesta_2 or not respuesta_3:
                errores.append('Debes completar las 3 opciones de respuesta.')
            if correcta not in ['1', '2', '3']:
                errores.append('Debes seleccionar cuál es la respuesta correcta.')

            if errores:
                return render(request, 'app_examen/crear_pregunta.html', {
                    'examen': examen,
                    'error': ' '.join(errores),
                    'form_data': request.POST,
                })

            try:
                with transaction.atomic():
                    pregunta = Pregunta.objects.create(
                        examen=examen,
                        contenido=contenido,
                        imagen=imagen,
                    )
                    for i, texto in enumerate([respuesta_1, respuesta_2, respuesta_3], 1):
                        Respuesta.objects.create(
                            pregunta=pregunta,
                            contenido=texto,
                            es_correcta=(str(i) == correcta),
                        )
            except Exception as e:
                return render(request, 'app_examen/crear_pregunta.html', {
                    'examen': examen,
                    'error': f'Error al guardar: {str(e)}',
                    'form_data': request.POST,
                })

            messages.success(request, 'Pregunta y respuestas creadas correctamente.')
            return redirect('app_examen:detalle_examen', examen_id=examen.id)

        return render(request, 'app_examen/crear_pregunta.html', {
            'examen': examen,
            'preguntas_existentes': preguntas_existentes,
        })
    
    @login_required
    @user_passes_test(es_superusuario, login_url='/acceso-denegado/')
    def editar_pregunta(request, pregunta_id):
        """Solo Superusuarios - Gestión del banco de preguntas"""
        pregunta = get_object_or_404(Pregunta, id=pregunta_id)
        respuestas = list(pregunta.respuestas.all().order_by('id'))

        # Datos iniciales para pre-llenar el formulario
        respuestas_iniciales = {
            'respuesta_1': respuestas[0].contenido if len(respuestas) > 0 else '',
            'respuesta_2': respuestas[1].contenido if len(respuestas) > 1 else '',
            'respuesta_3': respuestas[2].contenido if len(respuestas) > 2 else '',
        }
        correcta_actual = next((str(i) for i, r in enumerate(respuestas, 1) if r.es_correcta), None)

        if request.method == 'POST':
            contenido = request.POST.get('contenido', '').strip()
            imagen = request.FILES.get('imagen')
            respuesta_1 = request.POST.get('respuesta_1', '').strip()
            respuesta_2 = request.POST.get('respuesta_2', '').strip()
            respuesta_3 = request.POST.get('respuesta_3', '').strip()
            correcta = request.POST.get('correcta', '')

            errores = []
            if not contenido:
                errores.append('El contenido de la pregunta es obligatorio.')
            if not respuesta_1 or not respuesta_2 or not respuesta_3:
                errores.append('Debes completar las 3 opciones de respuesta.')
            if correcta not in ['1', '2', '3']:
                errores.append('Debes seleccionar cuál es la respuesta correcta.')

            if errores:
                return render(request, 'app_examen/editar_pregunta.html', {
                    'pregunta': pregunta,
                    'error': ' '.join(errores),
                    'form_data': request.POST,
                    'correcta_actual': request.POST.get('correcta'),
                })

            try:
                with transaction.atomic():
                    pregunta.contenido = contenido
                    if imagen:
                        pregunta.imagen = imagen
                    pregunta.save()

                    textos = [respuesta_1, respuesta_2, respuesta_3]

                    # Limpiar flags de correcta antes de actualizar (evita conflicto de validación)
                    pregunta.respuestas.update(es_correcta=False)

                    for i, texto in enumerate(textos, 1):
                        es_correcta = (str(i) == correcta)
                        if i <= len(respuestas):
                            r = respuestas[i - 1]
                            r.contenido = texto
                            r.es_correcta = es_correcta
                            r.save()
                        else:
                            Respuesta.objects.create(
                                pregunta=pregunta,
                                contenido=texto,
                                es_correcta=es_correcta,
                            )
            except Exception as e:
                return render(request, 'app_examen/editar_pregunta.html', {
                    'pregunta': pregunta,
                    'error': f'Error al guardar: {str(e)}',
                    'form_data': request.POST,
                    'correcta_actual': request.POST.get('correcta'),
                })

            messages.success(request, 'Pregunta y respuestas actualizadas correctamente.')
            return redirect('app_examen:detalle_examen', examen_id=pregunta.examen.id)

        return render(request, 'app_examen/editar_pregunta.html', {
            'pregunta': pregunta,
            'form_data': respuestas_iniciales,
            'correcta_actual': correcta_actual,
        })
    
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

