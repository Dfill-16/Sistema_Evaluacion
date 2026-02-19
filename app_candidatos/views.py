from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.db.models import Max, Q, Avg
from app_examen.models import ExamenCandidato
import random
import string

Usuario = get_user_model()

# Funciones auxiliares para verificar roles
def es_administrador(user):
    return user.is_authenticated and (user.rol == 'admin' or user.is_superuser)

def es_candidato(user):
    return user.is_authenticated and user.rol == 'candidato'


@login_required
@user_passes_test(es_administrador, login_url='/acceso-denegado/')
def registrar_candidato(request):
    """Solo Administradores"""
    if request.method == 'POST':
        # Obtener datos del formulario
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        documento = request.POST.get('documento')
        celular = request.POST.get('celular')
        foto = request.FILES.get('foto')
        
        # Generar contraseña aleatoria
        password = generar_password()
        
        try:
            # Crear usuario candidato
            candidato = Usuario.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                documento=documento,
                celular=celular,
                foto=foto,
                rol='candidato'
            )
            
            # Enviar correo con credenciales
            correo_enviado = enviar_credenciales_email(candidato, username, password)
            
            if correo_enviado:
                messages.success(request, f'Candidato {candidato.get_full_name()} registrado exitosamente. Se han enviado las credenciales por correo.')
            else:
                messages.warning(request, f'Candidato {candidato.get_full_name()} registrado, pero no se pudo enviar el correo de credenciales. Verifica la configuración de email.')
            return redirect('app_candidatos:lista_candidatos')
            
        except Exception as e:
            messages.error(request, f'Error al registrar candidato: {str(e)}')
    
    return render(request, 'app_candidatos/registrar_candidato.html')


@login_required
@user_passes_test(es_administrador, login_url='/acceso-denegado/')
def lista_candidatos(request):
    """Solo Administradores"""
    candidatos = Usuario.objects.filter(rol='candidato', is_superuser=False).order_by('-date_joined')
    
    # Estadísticas
    total_candidatos = candidatos.count()
    candidatos_activos = candidatos.filter(is_active=True).count()
    candidatos_inactivos = candidatos.filter(is_active=False).count()
    
    context = {
        'candidatos': candidatos,
        'total_candidatos': total_candidatos,
        'candidatos_activos': candidatos_activos,
        'candidatos_inactivos': candidatos_inactivos,
    }
    
    return render(request, 'app_candidatos/lista_candidatos.html', context)


@login_required
@user_passes_test(es_administrador, login_url='/acceso-denegado/')
def editar_candidato(request, candidato_id):
    """Solo Administradores"""
    candidato = get_object_or_404(Usuario, id=candidato_id, rol='candidato')
    
    if request.method == 'POST':
        candidato.first_name = request.POST.get('first_name')
        candidato.last_name = request.POST.get('last_name')
        candidato.email = request.POST.get('email')
        candidato.documento = request.POST.get('documento')
        candidato.celular = request.POST.get('celular')
        
        # Actualizar estado activo/inactivo
        candidato.is_active = request.POST.get('is_active') == 'on'
        
        foto = request.FILES.get('foto')
        if foto:
            candidato.foto = foto
        
        candidato.save()
        messages.success(request, f'Candidato {candidato.get_full_name()} actualizado exitosamente.')
        return redirect('app_candidatos:detalle_candidato', candidato_id=candidato.id)
    
    return render(request, 'app_candidatos/editar_candidato.html', {'candidato': candidato})


@login_required
@user_passes_test(es_administrador, login_url='/acceso-denegado/')
def eliminar_candidato(request, candidato_id):
    """Solo Administradores"""
    candidato = get_object_or_404(Usuario, id=candidato_id, rol='candidato')
    
    if request.method == 'POST':
        candidato.is_active = False
        candidato.save()
        messages.success(request, f'Candidato {candidato.get_full_name()} desactivado exitosamente.')
        return redirect('app_candidatos:lista_candidatos')
    
    return render(request, 'app_candidatos/eliminar_candidato.html', {'candidato': candidato})


@login_required
@user_passes_test(es_administrador, login_url='/acceso-denegado/')
def tabla_posiciones(request):
    """Solo Administradores"""
    from django.db.models import Avg
    
    # Obtener candidatos con sus mejores puntajes
    candidatos_con_puntaje = Usuario.objects.filter(
        rol='candidato',
        is_superuser=False,
        examenes_presentados__completado=True
    ).annotate(
        mejor_puntaje=Max('examenes_presentados__puntaje')
    ).order_by('-mejor_puntaje', 'last_name')
    
    # También incluir candidatos sin exámenes
    candidatos_sin_examen = Usuario.objects.filter(
        rol='candidato',
        is_superuser=False
    ).exclude(
        id__in=candidatos_con_puntaje.values_list('id', flat=True)
    ).order_by('last_name')
    
    # Estadísticas
    total_evaluados = candidatos_con_puntaje.count()
    sin_evaluar = candidatos_sin_examen.count()
    promedio_general = ExamenCandidato.objects.filter(completado=True).aggregate(
        promedio=Avg('puntaje')
    )['promedio']
    mejor_puntaje = candidatos_con_puntaje.first().mejor_puntaje if candidatos_con_puntaje.exists() else None
    
    context = {
        'candidatos_con_puntaje': candidatos_con_puntaje,
        'candidatos_sin_examen': candidatos_sin_examen,
        'total_evaluados': total_evaluados,
        'sin_evaluar': sin_evaluar,
        'promedio_general': promedio_general,
        'mejor_puntaje': mejor_puntaje,
    }
    
    return render(request, 'app_candidatos/tabla_posiciones.html', context)


@login_required
@user_passes_test(es_administrador, login_url='/acceso-denegado/')
def detalle_candidato(request, candidato_id):
    """Solo Administradores"""
    from django.db.models import Avg
    
    candidato = get_object_or_404(Usuario, id=candidato_id, rol='candidato')
    examenes_presentados = ExamenCandidato.objects.filter(
        candidato=candidato,
        completado=True
    ).select_related('examen').order_by('-fecha_presentacion')
    
    # Estadísticas del candidato
    examenes_count = examenes_presentados.count()
    promedio = examenes_presentados.aggregate(promedio=Avg('puntaje'))['promedio']
    mejor_puntaje = examenes_presentados.aggregate(mejor=Max('puntaje'))['mejor']
    
    context = {
        'candidato': candidato,
        'examenes_presentados': examenes_presentados,
        'examenes_count': examenes_count,
        'promedio': promedio,
        'mejor_puntaje': mejor_puntaje,
    }
    
    return render(request, 'app_candidatos/detalle_candidato.html', context)


@login_required
def dashboard_candidato(request):
    """Dashboard para candidatos - Vista principal después del login"""
    # Verificar que el usuario sea candidato
    if not es_candidato(request.user):
        messages.error(request, 'No tienes permisos para acceder a esta página.')
        return redirect('acceso_denegado')
    
    # Obtener exámenes disponibles y presentados por el candidato
    from app_examen.models import Examen
    
    examenes_disponibles = Examen.objects.filter(activo=True).exclude(
        examenes_candidatos__candidato=request.user
    )
    
    examenes_presentados = ExamenCandidato.objects.filter(
        candidato=request.user,
        completado=True
    ).select_related('examen').order_by('-fecha_presentacion')
    promedio = examenes_presentados.aggregate(promedio=Avg('puntaje'))['promedio']
    mejor_puntaje = examenes_presentados.aggregate(mejor=Max('puntaje'))['mejor']
    
    return render(request, 'candidato/dashboard.html', {
        'candidato': request.user,
        'examenes_disponibles': examenes_disponibles,
        'examenes_presentados': examenes_presentados,
        'promedio': promedio,
        'mejor_puntaje': mejor_puntaje,
    })


@login_required
@user_passes_test(es_candidato, login_url='/acceso-denegado/')
def mi_perfil(request):
    """Perfil de candidato: permite actualizar datos, foto y contraseña."""
    user = request.user
    if request.method == 'POST':
        cambio_datos = False

        # Actualizar datos básicos
        email = request.POST.get('email')
        celular = request.POST.get('celular')
        if email and email != user.email:
            user.email = email
            cambio_datos = True
        if celular is not None and celular != user.celular:
            user.celular = celular
            cambio_datos = True

        # Actualizar foto
        foto = request.FILES.get('foto')
        if foto:
            user.foto = foto
            cambio_datos = True

        # Cambiar contraseña
        password_actual = request.POST.get('password_actual')
        password_nueva = request.POST.get('password_nueva')
        password_confirmacion = request.POST.get('password_confirmacion')
        if password_nueva or password_confirmacion:
            if not password_actual or not user.check_password(password_actual):
                messages.error(request, 'La contraseña actual no es correcta.')
                return redirect('app_candidatos:mi_perfil')
            if password_nueva != password_confirmacion:
                messages.error(request, 'La confirmación de contraseña no coincide.')
                return redirect('app_candidatos:mi_perfil')
            user.set_password(password_nueva)
            cambio_datos = True
            messages.success(request, 'Contraseña actualizada correctamente. Vuelve a iniciar sesión.')

        if cambio_datos:
            user.save()
            # Si se cambió la contraseña, forzar logout más adelante; aquí solo informamos.
            if not (password_nueva or password_confirmacion):
                messages.success(request, 'Perfil actualizado correctamente.')

        return redirect('app_candidatos:mi_perfil')

    return render(request, 'candidato/mi_perfil.html')



# Funciones auxiliares
def generar_password(length=10):
    """Genera una contraseña aleatoria segura"""
    caracteres = string.ascii_letters + string.digits + "!@#$%"
    return ''.join(random.choice(caracteres) for _ in range(length))


def enviar_credenciales_email(candidato, username, password):
    """Envía correo electrónico con las credenciales al candidato. Retorna True si se envió."""
    if not candidato.email:
        print("No se envió correo: el candidato no tiene email configurado.")
        return False
    
    asunto = 'Credenciales de acceso - Sistema de Evaluación'
    mensaje = f"""
    Hola {candidato.get_full_name()},

    Se ha creado tu cuenta en el Sistema de Evaluación Virtual.
    
    Tus credenciales de acceso son:
    
    Usuario: {username}
    Contraseña: {password}
    
    Por favor, ingresa al sistema y cambia tu contraseña en tu primer acceso.
    
    URL de acceso: {settings.SITE_URL if hasattr(settings, 'SITE_URL') else 'http://localhost:8000'}
    
    Saludos,
    Equipo de Recursos Humanos
    """
    
    try:
        enviados = send_mail(
            asunto,
            mensaje,
            settings.DEFAULT_FROM_EMAIL,
            [candidato.email],
            fail_silently=False,
        )
        return enviados > 0
    except Exception as e:
        print(f"Error al enviar correo: {e}")
        return False
