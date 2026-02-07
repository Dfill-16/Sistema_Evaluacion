# ✅ Resumen de Cambios Implementados

## 📊 Base de Datos Optimizada y Lista

### 🎯 Cambios Realizados

#### 1. **Modelo de Usuario Unificado** (app_core/models.py)
**ANTES:** Dos modelos AbstractUser (Administrador y Candidato) → CONFLICTO
**AHORA:** Un solo modelo `Administrador` con campo `rol` 

```python
class Administrador(AbstractUser):
    ROLES = (
        ('admin', 'Administrador'),
        ('candidato', 'Candidato'),
    )
    rol = models.CharField(choices=ROLES, default='candidato')
    documento = models.CharField(unique=True)
    celular = models.CharField(unique=True)
    foto = models.ImageField(upload_to='usuarios/')  # ✅ MEDIA
    fecha_creacion = DateTimeField
    fecha_modificacion = DateTimeField
    
    # Propiedades útiles
    @property
    def es_administrador(self):
        return self.rol == 'admin' or self.is_superuser
    
    @property
    def es_candidato(self):
        return self.rol == 'candidato'
```

**Ventajas:**
- ✅ Sin conflictos de AbstractUser
- ✅ Un solo AUTH_USER_MODEL
- ✅ Fácil diferenciación por rol
- ✅ Campo foto incluido para todos

---

#### 2. **Modelos de Examen Completos** (app_examen/models.py)

##### Examen
```python
class Examen:
    nombre = CharField
    descripcion = TextField
    activo = BooleanField  # Control de activación
```

##### Pregunta
```python
class Pregunta:
    examen = ForeignKey(Examen, RESTRICT)
    contenido = TextField
    imagen = ImageField(upload_to='preguntas/')  # ✅ MEDIA
    orden = PositiveIntegerField  # Control de secuencia
```

##### Respuesta
```python
class Respuesta:
    pregunta = ForeignKey(Pregunta, RESTRICT)
    contenido = TextField
    es_correcta = BooleanField
    
    # Validar en admin: MAX 3 por pregunta, SOLO 1 correcta
```

##### ⭐ ExamenCandidato (Tabla Muchos a Muchos)
```python
class ExamenCandidato:
    candidato = ForeignKey(settings.AUTH_USER_MODEL, CASCADE)
    examen = ForeignKey(Examen, CASCADE)
    puntaje = DecimalField(5,2)
    fecha_presentacion = DateTimeField
    completado = BooleanField
    tiempo_empleado = DurationField
    
    UNIQUE_TOGETHER: (candidato, examen)  # ✅ Evita reintento
```

##### RespuestaCandidato
```python
class RespuestaCandidato:
    examen_candidato = ForeignKey(ExamenCandidato)
    pregunta = ForeignKey(Pregunta)
    respuesta_seleccionada = ForeignKey(Respuesta)
    es_correcta = BooleanField
    fecha_respuesta = DateTimeField
    
    UNIQUE_TOGETHER: (examen_candidato, pregunta)
```

---

#### 3. **Configuración MEDIA (settings.py)**

```python
# Static files (logos, CSS, JS)
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

# Media files (archivos subidos) - Equivalente a 'storage' en Laravel
MEDIA_URL = '/storage/'
MEDIA_ROOT = BASE_DIR / 'storage'  # ✅ Como Laravel
```

**Carpetas que se crearán automáticamente:**
```
storage/
├── usuarios/       (fotos de candidatos y admins)
└── preguntas/      (imágenes en preguntas)
```

---

#### 4. **URLs para Servir Media (urls.py)**

```python
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
]

# Servir archivos media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

---

## 🚀 Próximos Pasos

### 1. Aplicar Migraciones a la Base de Datos
```bash
# Activar entorno virtual (si no está activo)
.\venv\Scripts\Activate.ps1

# Aplicar migraciones
python manage.py migrate
```

### 2. Crear Superusuario
```bash
python manage.py createsuperuser
# Username: admin
# Email: admin@ejemplo.com
# Password: (tu contraseña segura)
```

### 3. Configurar Admin de Django

Crear `app_examen/admin.py`:

```python
from django.contrib import admin
from django.core.exceptions import ValidationError
from .models import Examen, Pregunta, Respuesta, ExamenCandidato, RespuestaCandidato

class RespuestaInline(admin.TabularInline):
    model = Respuesta
    extra = 3
    max_num = 3  # ✅ Máximo 3 opciones
    min_num = 3  # ✅ Mínimo 3 opciones
    
    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        
        # Validar solo 1 correcta
        original_clean = formset.clean
        def clean_with_validation():
            original_clean()
            correctas = sum(1 for form in formset.forms 
                          if form.cleaned_data.get('es_correcta'))
            if correctas != 1:
                raise ValidationError('Debe haber exactamente 1 respuesta correcta')
        
        formset.clean = clean_with_validation
        return formset

class PreguntaAdmin(admin.ModelAdmin):
    inlines = [RespuestaInline]
    list_display = ['id', 'contenido_breve', 'examen', 'orden', 'tiene_imagen']
    list_filter = ['examen']
    search_fields = ['contenido']
    list_editable = ['orden']
    
    def contenido_breve(self, obj):
        return obj.contenido[:50] + '...' if len(obj.contenido) > 50 else obj.contenido
    contenido_breve.short_description = 'Contenido'
    
    def tiene_imagen(self, obj):
        return '✅' if obj.imagen else '❌'
    tiene_imagen.short_description = 'Imagen'

class ExamenAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'activo', 'cantidad_preguntas', 'fecha_creacion']
    list_filter = ['activo', 'fecha_creacion']
    search_fields = ['nombre', 'descripcion']
    list_editable = ['activo']
    
    def cantidad_preguntas(self, obj):
        return obj.preguntas.count()
    cantidad_preguntas.short_description = 'N° Preguntas'

class ExamenCandidatoAdmin(admin.ModelAdmin):
    list_display = ['candidato', 'examen', 'puntaje', 'completado', 'fecha_presentacion']
    list_filter = ['completado', 'examen', 'fecha_presentacion']
    search_fields = ['candidato__username', 'candidato__documento']
    readonly_fields = ['fecha_presentacion']

admin.site.register(Examen, ExamenAdmin)
admin.site.register(Pregunta, PreguntaAdmin)
admin.site.register(ExamenCandidato, ExamenCandidatoAdmin)
admin.site.register(RespuestaCandidato)
```

Crear `app_core/admin.py`:

```python
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Administrador

class AdministradorAdmin(UserAdmin):
    list_display = ['username', 'email', 'rol', 'documento', 'es_staff_user', 'fecha_creacion']
    list_filter = ['rol', 'is_staff', 'is_superuser', 'fecha_creacion']
    search_fields = ['username', 'email', 'documento', 'first_name', 'last_name']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Información Adicional', {
            'fields': ('rol', 'documento', 'celular', 'foto')
        }),
        ('Fechas', {
            'fields': ('fecha_creacion', 'fecha_modificacion')
        }),
    )
    
    readonly_fields = ['fecha_creacion', 'fecha_modificacion']
    
    def es_staff_user(self, obj):
        return '✅' if obj.is_staff else '❌'
    es_staff_user.short_description = 'Staff'

admin.site.register(Administrador, AdministradorAdmin)
```

### 4. Configurar Email (settings.py)

Para envío de credenciales a candidatos:

```python
# Desarrollo (consola)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Producción (Gmail ejemplo)
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'smtp.gmail.com'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = env('EMAIL_HOST_USER')
# EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')
# DEFAULT_FROM_EMAIL = 'Sistema de Evaluación <noreply@ejemplo.com>'
```

---

## 📋 Checklist de Implementación

### Base de Datos y Modelos
- [x] Modelo Usuario unificado (app_core.Administrador)
- [x] Campo `rol` para diferenciar admin/candidato
- [x] Campo `foto` en usuario (ImageField)
- [x] Modelo Examen con control de activación
- [x] Modelo Pregunta con soporte para imagen
- [x] Modelo Respuesta (validar 3 opciones, 1 correcta)
- [x] Modelo ExamenCandidato (relación M:M normalizada)
- [x] Modelo RespuestaCandidato (auditoría de respuestas)
- [x] Migraciones creadas exitosamente

### Configuración
- [x] MEDIA_ROOT = 'storage' (como Laravel)
- [x] MEDIA_URL = '/storage/'
- [x] URLs configuradas para servir media
- [x] Pillow instalado
- [x] Apps registradas en INSTALLED_APPS

### Pendiente
- [ ] Aplicar migraciones (`python manage.py migrate`)
- [ ] Crear superusuario
- [ ] Configurar admin.py en ambas apps
- [ ] Configurar EMAIL_BACKEND
- [ ] Crear vistas de login/logout
- [ ] Crear vistas para administrador (registro candidatos, tabla posiciones)
- [ ] Crear vistas para candidato (presentar examen)
- [ ] Implementar decoradores de permisos
- [ ] Crear templates con Bootstrap
- [ ] Agregar archivos estáticos (logo, CSS)

---

## 🎯 Uso de la Base de Datos

### Crear Candidato desde Vista Administrador
```python
from app_core.models import Administrador
from django.core.mail import send_mail
import random
import string

def registrar_candidato(request):
    if request.method == 'POST':
        # Generar contraseña aleatoria
        password = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
        
        candidato = Administrador.objects.create_user(
            username=request.POST['username'],
            email=request.POST['email'],
            password=password,
            rol='candidato',
            documento=request.POST['documento'],
            celular=request.POST.get('celular'),
            first_name=request.POST.get('first_name', ''),
            last_name=request.POST.get('last_name', ''),
        )
        
        if request.FILES.get('foto'):
            candidato.foto = request.FILES['foto']
            candidato.save()
        
        # Enviar credenciales por email
        send_mail(
            'Credenciales de Acceso - Sistema de Evaluación',
            f'Hola {candidato.first_name},\n\n'
            f'Tu usuario: {candidato.username}\n'
            f'Tu contraseña: {password}\n\n'
            f'Ingresa en: http://localhost:8000/login/',
            'noreply@ejemplo.com',
            [candidato.email],
            fail_silently=False,
        )
        
        return redirect('tabla_posiciones')
```

### Tabla de Posiciones
```python
from app_examen.models import ExamenCandidato

def tabla_posiciones(request):
    # Solo candidatos que completaron examen
    posiciones = ExamenCandidato.objects.filter(
        completado=True,
        candidato__rol='candidato'
    ).select_related('candidato', 'examen').order_by('-puntaje')
    
    return render(request, 'admin/tabla_posiciones.html', {
        'posiciones': posiciones
    })
```

### Verificar Intento de Candidato
```python
def vista_examen(request, examen_id):
    examen = get_object_or_404(Examen, id=examen_id, activo=True)
    
    # Verificar si ya presentó
    intento_previo = ExamenCandidato.objects.filter(
        candidato=request.user,
        examen=examen,
        completado=True
    ).first()
    
    if intento_previo:
        return render(request, 'candidato/ya_presento.html', {
            'puntaje': intento_previo.puntaje,
            'fecha': intento_previo.fecha_presentacion
        })
    
    # Continuar con examen...
```

---

## 📚 Documentación Adicional

- **GUIA_MEDIA_DJANGO_VS_LARAVEL.md**: Comparación detallada del manejo de archivos
- **ANALISIS_BASE_DATOS.md**: Análisis completo de cumplimiento de requerimientos

---

## ✅ Conclusión

Tu base de datos está **completamente configurada y lista** para:

1. ✅ **Múltiples apps Django** (app_core, app_candidatos, app_examen)
2. ✅ **Relación Muchos a Muchos normalizada** (ExamenCandidato)
3. ✅ **Soporte para imágenes** en candidatos y preguntas
4. ✅ **Restricción de un solo intento** (unique_together)
5. ✅ **Trazabilidad completa** de respuestas
6. ✅ **MEDIA_ROOT como 'storage'** (equivalente a Laravel)
7. ✅ **Diferenciación por roles** (admin/candidato)

**Siguiente paso:** Ejecuta `python manage.py migrate` y comienza a desarrollar las vistas y templates. 🚀
