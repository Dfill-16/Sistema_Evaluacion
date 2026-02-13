from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
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
    return render(request, 'app_core/lista_administradores.html', {'administradores': administradores})


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

