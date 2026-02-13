from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.db.models import Max, Q
from app_examen.models import ExamenCandidato
import random
import string

Usuario = get_user_model()

# Funciones auxiliares para verificar roles
def es_administrador(user):
    return user.is_authenticated and (user.rol == 'admin' or user.is_superuser)


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
            enviar_credenciales_email(candidato, username, password)
            
            messages.success(request, f'Candidato {candidato.get_full_name()} registrado exitosamente. Se han enviado las credenciales por correo.')
            return redirect('app_candidatos:lista_candidatos')
            
        except Exception as e:
            messages.error(request, f'Error al registrar candidato: {str(e)}')
    
    return render(request, 'app_candidatos/registrar_candidato.html')


@login_required
@user_passes_test(es_administrador, login_url='/acceso-denegado/')
def lista_candidatos(request):
    """Solo Administradores"""
    candidatos = Usuario.objects.filter(rol='candidato').order_by('-fecha_creacion')
    return render(request, 'app_candidatos/lista_candidatos.html', {'candidatos': candidatos})


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
        
        foto = request.FILES.get('foto')
        if foto:
            candidato.foto = foto
        
        candidato.save()
        messages.success(request, f'Candidato {candidato.get_full_name()} actualizado exitosamente.')
        return redirect('app_candidatos:lista_candidatos')
    
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
    # Obtener candidatos con sus mejores puntajes
    candidatos_con_puntaje = Usuario.objects.filter(
        rol='candidato',
        examenes_presentados__completado=True
    ).annotate(
        mejor_puntaje=Max('examenes_presentados__puntaje')
    ).order_by('-mejor_puntaje', 'last_name')
    
    # También incluir candidatos sin exámenes
    candidatos_sin_examen = Usuario.objects.filter(
        rol='candidato'
    ).exclude(
        id__in=candidatos_con_puntaje.values_list('id', flat=True)
    ).order_by('last_name')
    
    return render(request, 'app_candidatos/tabla_posiciones.html', {
        'candidatos_con_puntaje': candidatos_con_puntaje,
        'candidatos_sin_examen': candidatos_sin_examen
    })


@login_required
@user_passes_test(es_administrador, login_url='/acceso-denegado/')
def detalle_candidato(request, candidato_id):
    """Solo Administradores"""
    candidato = get_object_or_404(Usuario, id=candidato_id, rol='candidato')
    examenes_presentados = ExamenCandidato.objects.filter(
        candidato=candidato,
        completado=True
    ).select_related('examen').order_by('-fecha_presentacion')
    
    return render(request, 'app_candidatos/detalle_candidato.html', {
        'candidato': candidato,
        'examenes_presentados': examenes_presentados
    })


# Funciones auxiliares
def generar_password(length=10):
    """Genera una contraseña aleatoria segura"""
    caracteres = string.ascii_letters + string.digits + "!@#$%"
    return ''.join(random.choice(caracteres) for _ in range(length))


def enviar_credenciales_email(candidato, username, password):
    """Envía correo electrónico con las credenciales al candidato"""
    
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
        send_mail(
            asunto,
            mensaje,
            settings.DEFAULT_FROM_EMAIL,
            [candidato.email],
            fail_silently=False,
        )
    except Exception as e:
        print(f"Error al enviar correo: {e}")
        # No lanzar excepción para no bloquear el registro

