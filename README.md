# 🎓 Sistema de Evaluación Virtual Multipropósito

Sistema de gestión de exámenes en línea desarrollado con Django 5.2, diseñado para que empresas de recursos humanos puedan evaluar candidatos de manera eficiente y transparente.

## 📋 Características Principales

✅ **Gestión de Usuarios por Roles**
- Administradores: Pueden registrar candidatos y ver tabla de posiciones
- Candidatos: Pueden presentar exámenes una sola vez

✅ **Banco de Preguntas**
- Soporte para preguntas con imágenes
- 3 opciones de respuesta por pregunta (solo 1 correcta)
- Organización por exámenes

✅ **Sistema de Evaluación**
- Restricción de un solo intento por candidato
- Cálculo automático de puntaje
- Auditoría completa de respuestas

✅ **Gestión de Archivos Media**
- Fotos de candidatos
- Imágenes en preguntas
- Almacenamiento en carpeta `storage/` (equivalente a Laravel)

---

## 🚀 Instalación

### 1. Clonar el repositorio
```bash
git clone <url-repositorio>
cd Sistema_Evaluacion
```

### 2. Crear y activar entorno virtual
```bash
# Windows
python -m venv venv
.\venv\Scripts\Activate.ps1

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar base de datos
Editar archivo `.env` en la raíz del proyecto:
```env
DB_NAME=nombre_base_datos
DB_USER=usuario
DB_PASSWORD=contraseña
DB_HOST=localhost
DB_PORT=3306
```

### 5. Aplicar migraciones
```bash
python manage.py migrate
```

### 6. Crear superusuario
```bash
python manage.py createsuperuser
```

### 7. Crear carpetas necesarias
```bash
# Windows
mkdir static\img
mkdir static\css
mkdir static\js

# Linux/Mac
mkdir -p static/img static/css static/js
```

### 8. Ejecutar servidor
```bash
python manage.py runserver
```

Acceder a: http://localhost:8000/admin/

---

## 📁 Estructura del Proyecto

```
Sistema_Evaluacion/
├── app_RH/                 # Configuración principal
│   ├── settings.py         # Configuración Django
│   ├── urls.py             # URLs principales
│   └── wsgi.py
├── app_core/               # Usuarios (Administrador/Candidato)
│   ├── models.py           # Modelo Usuario único con rol
│   ├── views.py
│   └── admin.py
├── app_candidatos/         # Lógica de candidatos
│   ├── models.py
│   ├── views.py
│   └── urls.py
├── app_examen/             # Exámenes, preguntas, respuestas
│   ├── models.py           # Examen, Pregunta, Respuesta, ExamenCandidato
│   ├── views.py
│   └── admin.py
├── storage/                # Archivos media (MEDIA_ROOT)
│   ├── usuarios/           # Fotos de candidatos
│   └── preguntas/          # Imágenes de preguntas
├── static/                 # Archivos estáticos
│   ├── css/
│   ├── js/
│   └── img/                # Logo, avatares por defecto
├── staticfiles/            # Archivos recolectados (producción)
├── templates/              # Templates HTML
├── manage.py
├── requirements.txt
├── .env
└── .gitignore
```

---

## 🗄️ Modelos de Base de Datos

### Usuario (app_core.Administrador)
```python
- username (único)
- email
- rol (admin/candidato)
- documento (cédula, único)
- celular
- foto (ImageField → storage/usuarios/)
- fecha_creacion
```

### Examen
```python
- nombre
- descripcion
- activo (BooleanField)
- fecha_creacion
```

### Pregunta
```python
- examen (ForeignKey)
- contenido
- imagen (ImageField → storage/preguntas/)
- orden
```

### Respuesta
```python
- pregunta (ForeignKey)
- contenido
- es_correcta (BooleanField)
```

### ExamenCandidato (Relación M:M)
```python
- candidato (ForeignKey)
- examen (ForeignKey)
- puntaje (DecimalField)
- fecha_presentacion
- completado (BooleanField)
- tiempo_empleado (DurationField)
- UNIQUE_TOGETHER: (candidato, examen)  # Evita reintento
```

### RespuestaCandidato
```python
- examen_candidato (ForeignKey)
- pregunta (ForeignKey)
- respuesta_seleccionada (ForeignKey)
- es_correcta (BooleanField)
- fecha_respuesta
```

---

## 🔐 Roles y Permisos

### Superusuario
- Acceso completo al Admin de Django
- Gestión del banco de preguntas
- Creación de usuarios administradores

### Administrador (rol='admin')
- Registrar nuevos candidatos
- Ver tabla de posiciones global
- Envío automático de credenciales por email

### Candidato (rol='candidato')
- Presentar examen (una sola vez)
- Ver su puntaje
- Editar perfil

---

## 📝 Configuración de Email

### Desarrollo (Consola)
En `settings.py` ya está configurado:
```python
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

### Producción (Gmail)
En `settings.py`:
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = env('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = 'Sistema <noreply@ejemplo.com>'
```

En `.env`:
```env
EMAIL_HOST_USER=tu-email@gmail.com
EMAIL_HOST_PASSWORD=tu-contraseña-app
```

---

## 📚 Documentación Adicional

- **GUIA_MEDIA_DJANGO_VS_LARAVEL.md**: Comparación detallada de manejo de archivos media entre Django y Laravel
- **ANALISIS_BASE_DATOS.md**: Análisis completo del cumplimiento de requerimientos
- **RESUMEN_CAMBIOS.md**: Cambios implementados y configuración paso a paso
- **EJEMPLOS_TEMPLATES.md**: Ejemplos prácticos de uso de imágenes en templates HTML

---

## 🧪 Pruebas Básicas

### 1. Crear Examen de Prueba
```bash
python manage.py shell
```

```python
from app_examen.models import Examen, Pregunta, Respuesta

# Crear examen
examen = Examen.objects.create(nombre="Examen de Python", activo=True)

# Crear pregunta
pregunta = Pregunta.objects.create(
    examen=examen,
    contenido="¿Cuál es el framework web más popular de Python?",
    orden=1
)

# Crear respuestas (3 opciones, 1 correcta)
Respuesta.objects.create(pregunta=pregunta, contenido="Django", es_correcta=True)
Respuesta.objects.create(pregunta=pregunta, contenido="Flask", es_correcta=False)
Respuesta.objects.create(pregunta=pregunta, contenido="FastAPI", es_correcta=False)
```

### 2. Crear Usuario Candidato
```python
from app_core.models import Administrador

candidato = Administrador.objects.create_user(
    username='candidato1',
    email='candidato@ejemplo.com',
    password='password123',
    rol='candidato',
    documento='1234567890',
    first_name='Juan',
    last_name='Pérez'
)
```

---

## 🛠️ Comandos Útiles

```bash
# Crear migraciones
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Ejecutar servidor
python manage.py runserver

# Shell interactivo
python manage.py shell

# Recolectar archivos estáticos (producción)
python manage.py collectstatic

# Ver usuarios registrados
python manage.py shell -c "from app_core.models import Administrador; print(Administrador.objects.all())"
```

---

## 📊 Endpoints Principales (Pendiente Implementar)

### Públicos
- `GET /` - Página de inicio
- `GET /login/` - Login unificado (Admin/Candidato)
- `POST /login/` - Autenticación
- `GET /logout/` - Cerrar sesión

### Administrador
- `GET /admin/candidatos/registrar/` - Formulario registro candidato
- `POST /admin/candidatos/registrar/` - Guardar candidato
- `GET /admin/posiciones/` - Tabla de posiciones global

### Candidato
- `GET /candidato/dashboard/` - Dashboard candidato
- `GET /candidato/examen/<id>/` - Vista de examen
- `POST /candidato/examen/<id>/` - Enviar respuestas
- `GET /candidato/resultado/` - Ver puntaje

---

## 🚀 Despliegue en Producción

### 1. Configurar settings.py
```python
DEBUG = False
ALLOWED_HOSTS = ['tu-dominio.com', 'www.tu-dominio.com']

# Servir archivos estáticos
STATIC_ROOT = '/var/www/proyecto/static/'
MEDIA_ROOT = '/var/www/proyecto/storage/'
```

### 2. Recolectar archivos estáticos
```bash
python manage.py collectstatic --noinput
```

### 3. Configurar Nginx
```nginx
server {
    listen 80;
    server_name tu-dominio.com;

    location /static/ {
        alias /var/www/proyecto/static/;
    }

    location /storage/ {
        alias /var/www/proyecto/storage/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 🤝 Contribuciones

Este proyecto fue desarrollado como parte del **Ejercicio Integrador 1** del curso de programación.

**Fecha de entrega:** 06/02/2026  
**Fecha de sustentación:** 20/02/2026

---

## 📄 Licencia

Este proyecto es de uso educativo.

---

## 👤 Autor

Desarrollado por estudiantes de ADSO 2026

---

## 📞 Soporte

Para dudas o problemas, consultar la documentación adicional en los archivos `.md` del proyecto.
