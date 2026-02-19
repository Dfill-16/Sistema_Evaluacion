from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import get_user_model, authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
import random
import string

Usuario = get_user_model()

# Función auxiliar para verificar superusuario
def es_superusuario(user):
    return user.is_authenticated and user.is_superuser


@login_required
@user_passes_test(es_superusuario, login_url='/acceso-denegado/')
def registrar_administrador(request):
    """Solo Superusuarios - Registrar nuevo administrador"""
    if request.method == 'POST':
        # Obtener datos del formulario
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        documento = request.POST.get('documento')
        celular = request.POST.get('celular')
        foto = request.FILES.get('foto')
        
        # Generar contraseña aleatoria o usar la proporcionada
        password = request.POST.get('password')
        if not password:
            password = generar_password()
        
        try:
            # Crear usuario administrador
            administrador = Usuario.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                documento=documento,
                celular=celular,
                foto=foto,
                rol='admin'
            )
            enviar_credenciales_email(administrador, username, password)
            
            messages.success(request, f'Administrador {administrador.get_full_name()} registrado exitosamente.')
            return redirect('app_core:lista_administradores')
            
        except Exception as e:
            messages.error(request, f'Error al registrar administrador: {str(e)}')
    
    return render(request, 'app_core/registrar_administrador.html')


@login_required
@user_passes_test(es_superusuario, login_url='/acceso-denegado/')
def lista_administradores(request):
    """Solo Superusuarios - Listar todos los administradores"""
    administradores = Usuario.objects.filter(rol='admin').order_by('-fecha_creacion')
    context = {
        'administradores': administradores,
        'total_admins': administradores.count(),
        'activos_admins': administradores.filter(is_active=True).count(),
        'inactivos_admins': administradores.filter(is_active=False).count(),
    }
    return render(request, 'app_core/lista_administradores.html', context)


@login_required
@user_passes_test(es_superusuario, login_url='/acceso-denegado/')
def detalle_administrador(request, admin_id):
    """Solo Superusuarios - Ver detalle de administrador"""
    administrador = get_object_or_404(Usuario, id=admin_id, rol='admin')
    return render(request, 'app_core/detalle_administrador.html', {'administrador': administrador})


@login_required
@user_passes_test(es_superusuario, login_url='/acceso-denegado/')
def editar_administrador(request, admin_id):
    """Solo Superusuarios - Editar datos de administrador"""
    administrador = get_object_or_404(Usuario, id=admin_id, rol='admin')
    
    if request.method == 'POST':
        administrador.username = request.POST.get('username')
        administrador.first_name = request.POST.get('first_name')
        administrador.last_name = request.POST.get('last_name')
        administrador.email = request.POST.get('email')
        administrador.documento = request.POST.get('documento')
        administrador.celular = request.POST.get('celular')
        
        # Actualizar contraseña solo si se proporciona
        nueva_password = request.POST.get('password')
        if nueva_password:
            administrador.set_password(nueva_password)
        
        foto = request.FILES.get('foto')
        if foto:
            administrador.foto = foto
        
        try:
            administrador.save()
            messages.success(request, f'Administrador {administrador.get_full_name()} actualizado exitosamente.')
            return redirect('app_core:lista_administradores')
        except Exception as e:
            messages.error(request, f'Error al actualizar administrador: {str(e)}')
    
    return render(request, 'app_core/editar_administrador.html', {'administrador': administrador})


@login_required
@user_passes_test(es_superusuario, login_url='/acceso-denegado/')
def eliminar_administrador(request, admin_id):
    """Solo Superusuarios - Eliminar (desactivar) administrador"""
    administrador = get_object_or_404(Usuario, id=admin_id, rol='admin')
    
    # Prevenir que el superusuario se elimine a sí mismo
    if administrador.id == request.user.id:
        messages.error(request, 'No puedes desactivar tu propia cuenta.')
        return redirect('app_core:lista_administradores')
    
    if request.method == 'POST':
        administrador.is_active = False
        administrador.save()
        messages.success(request, f'Administrador {administrador.get_full_name()} desactivado exitosamente.')
        return redirect('app_core:lista_administradores')
    
    return render(request, 'app_core/eliminar_administrador.html', {'administrador': administrador})


@login_required
@user_passes_test(es_superusuario, login_url='/acceso-denegado/')
def activar_administrador(request, admin_id):
    """Solo Superusuarios - Reactivar administrador desactivado"""
    administrador = get_object_or_404(Usuario, id=admin_id, rol='admin')
    
    if request.method == 'POST':
        administrador.is_active = True
        administrador.save()
        messages.success(request, f'Administrador {administrador.get_full_name()} reactivado exitosamente.')
        return redirect('app_core:lista_administradores')
    
    return render(request, 'app_core/activar_administrador.html', {'administrador': administrador})


# Funciones auxiliares
def generar_password(length=10):
    """Genera una contraseña aleatoria segura"""
    caracteres = string.ascii_letters + string.digits + "!@#$%"
    return ''.join(random.choice(caracteres) for _ in range(length))


def enviar_credenciales_email(usuario, username, password):
    """Envía correo electrónico con las credenciales al nuevo usuario"""
    asunto = 'Credenciales de acceso - Sistema de Evaluación'
    mensaje = f"""
    Hola {usuario.get_full_name() or usuario.username},

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
            [usuario.email],
            fail_silently=False,
        )
    except Exception as e:
        print(f"Error al enviar correo de credenciales: {e}")


# ============================
# AUTENTICACIÓN
# ============================

def login_view(request):
    """Vista de login para todos los usuarios"""
    if request.user.is_authenticated:
        # Redirigir según el tipo de usuario
        if request.user.is_superuser:
            return redirect('/admin/')  # Panel Django Admin
        elif request.user.es_administrador:
            return redirect('app_core:dashboard_administrador')  # Dashboard admin
        else:
            return redirect('app_candidatos:dashboard_candidato')  # Dashboard candidato
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            if user.is_active:
                login(request, user)
                messages.success(request, f'¡Bienvenido, {user.get_full_name() or user.username}!')
                
                # Redirigir según el rol
                next_url = request.GET.get('next')
                if next_url:
                    return redirect(next_url)
                
                if user.is_superuser:
                    return redirect('/admin/')  # Panel Django Admin
                elif user.es_administrador:
                    return redirect('app_core:dashboard_administrador')  # Dashboard admin
                else:
                    return redirect('app_candidatos:dashboard_candidato')  # Dashboard candidato
            else:
                messages.error(request, 'Tu cuenta está desactivada.')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')
    
    return render(request, 'auth/login.html')


@login_required
def logout_view(request):
    """Cerrar sesión"""
    logout(request)
    messages.info(request, 'Has cerrado sesión correctamente.')
    return redirect('login')


def acceso_denegado(request):
    """Página de acceso denegado"""
    return render(request, 'auth/acceso_denegado.html')


# ============================
# DASHBOARD ADMINISTRADOR
# ============================

def es_administrador(user):
    """Verifica si el usuario es administrador o superusuario"""
    return user.is_authenticated and (user.rol == 'admin' or user.is_superuser)


@login_required
@user_passes_test(es_administrador, login_url='/acceso-denegado/')
def dashboard_administrador(request):
    """Dashboard principal para administradores"""
    from django.db.models import Count, Avg
    from app_examen.models import ExamenCandidato
    from django.utils import timezone
    
    # Estadísticas generales
    total_candidatos = Usuario.objects.filter(rol='candidato').count()
    candidatos_activos = Usuario.objects.filter(rol='candidato', is_active=True).count()
    examenes_presentados = ExamenCandidato.objects.filter(completado=True).count()
    
    # Promedio general de puntajes
    promedio_general = ExamenCandidato.objects.filter(completado=True).aggregate(
        promedio=Avg('puntaje')
    )['promedio']
    
    # Candidatos sin examen
    candidatos_sin_examen = Usuario.objects.filter(
        rol='candidato'
    ).exclude(
        examenes_presentados__completado=True
    ).count()
    
    # Últimos 5 candidatos registrados
    ultimos_candidatos = Usuario.objects.filter(
        rol='candidato'
    ).order_by('-date_joined')[:5]
    
    # Fecha actual
    now = timezone.now()
    
    context = {
        'total_candidatos': total_candidatos,
        'candidatos_activos': candidatos_activos,
        'examenes_presentados': examenes_presentados,
        'promedio_general': promedio_general,
        'candidatos_sin_examen': candidatos_sin_examen,
        'ultimos_candidatos': ultimos_candidatos,
        'now': now,
    }
    
    return render(request, 'administrador/dashboard.html', context)

