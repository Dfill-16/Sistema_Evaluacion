# 📊 Análisis de Base de Datos - Sistema de Evaluación

## ✅ Cumplimiento de Requerimientos

### 1. ✅ Arquitectura en Múltiples Apps Django

- **app_core**: Modelo Administrador (usuarios admin)
- **app_candidatos**: Modelo Candidato (usuarios candidatos con foto)
- **app_examen**: Modelos Examen, Pregunta, Respuesta, ExamenCandidato, RespuestaCandidato

### 2. ✅ Gestión de Archivos Media

- **Candidatos**: Campo `foto` con `upload_to='candidatos/'`
- **Preguntas**: Campo `imagen` con `upload_to='preguntas/'`
- **Configuración**: MEDIA_ROOT = 'storage' (equivalente a Laravel)

### 3. ✅ Relación Muchos a Muchos Normalizada

- **Modelo ExamenCandidato**: Tabla intermedia con datos adicionales
  - Guarda: puntaje, fecha_presentacion, tiempo_empleado, completado
  - Restricción: unique_together para evitar duplicados
  - Relación: Un candidato puede presentar múltiples exámenes

### 4. ✅ Banco de Preguntas con 3 Opciones

- **Modelo Pregunta**: Vinculado a Examen
- **Modelo Respuesta**: 3 respuestas por pregunta (validar en admin)
- **Campo es_correcta**: Marca la respuesta correcta

---

## 🗄️ Estructura de la Base de Datos

### Diagrama Relacional

```
┌─────────────────────┐
│   Administrador     │
│  (AbstractUser)     │
│─────────────────────│
│ id (PK)             │
│ username            │
│ email               │
│ documento           │
│ celular             │
└─────────────────────┘

┌─────────────────────┐         ┌─────────────────────┐
│    Candidato        │         │      Examen         │
│  (AbstractUser)     │         │─────────────────────│
│─────────────────────│         │ id (PK)             │
│ id (PK)             │         │ nombre              │
│ username            │         │ descripcion         │
│ email               │         │ activo              │
│ documento           │         │ fecha_creacion      │
│ telefono            │         └─────────────────────┘
│ foto (MEDIA)        │                  │
│ fecha_creacion      │                  │ 1:N
└─────────────────────┘                  ▼
         │                     ┌─────────────────────┐
         │ N:M                 │     Pregunta        │
         │                     │─────────────────────│
         │                     │ id (PK)             │
         │                     │ examen_id (FK)      │
         │                     │ contenido           │
         │                     │ imagen (MEDIA)      │
         │                     │ orden               │
         │                     └─────────────────────┘
         │                              │
         │                              │ 1:3
         │                              ▼
         │                     ┌─────────────────────┐
         │                     │     Respuesta       │
         │                     │─────────────────────│
         │                     │ id (PK)             │
         │                     │ pregunta_id (FK)    │
         │                     │ contenido           │
         │                     │ es_correcta         │
         │                     └─────────────────────┘
         │
         │
         └────────┐
                  ▼
         ┌─────────────────────┐
         │ ExamenCandidato     │
         │   (Tabla M:M)       │
         │─────────────────────│
         │ id (PK)             │
         │ candidato_id (FK)   │
         │ examen_id (FK)      │
         │ puntaje             │
         │ fecha_presentacion  │
         │ completado          │
         │ tiempo_empleado     │
         │ UNIQUE(candidato,   │
         │        examen)      │
         └─────────────────────┘
                  │
                  │ 1:N
                  ▼
         ┌─────────────────────┐
         │ RespuestaCandidato  │
         │─────────────────────│
         │ id (PK)             │
         │ examen_candidato(FK)│
         │ pregunta_id (FK)    │
         │ respuesta_selec(FK) │
         │ es_correcta         │
         │ fecha_respuesta     │
         │ UNIQUE(examen_cand, │
         │        pregunta)    │
         └─────────────────────┘
```

---

## 📋 Modelos Implementados

### 1. Candidato (app_candidatos)

```python
class Candidato(AbstractUser):
    documento = CharField (unique)
    telefono = CharField (unique)
    foto = ImageField (storage/candidatos/)  ✅ MEDIA
    fecha_creacion = DateTimeField
    fecha_modificacion = DateTimeField
```

**Funcionalidad:**

- ✅ Autenticación mediante AbstractUser
- ✅ Foto de perfil para tabla de posiciones
- ✅ Documento para identificación única

---

### 2. Examen (app_examen)

```python
class Examen:
    nombre = CharField
    descripcion = TextField
    activo = BooleanField
    fecha_creacion = DateTimeField
    fecha_modificacion = DateTimeField
```

**Funcionalidad:**

- ✅ Gestión de múltiples exámenes
- ✅ Control de activación/desactivación

---

### 3. Pregunta (app_examen)

```python
class Pregunta:
    examen = ForeignKey(Examen)  → RESTRICT
    contenido = TextField
    imagen = ImageField (storage/preguntas/)  ✅ MEDIA
    orden = PositiveIntegerField
```

**Funcionalidad:**

- ✅ Soporte para imágenes en preguntas
- ✅ Orden personalizable para presentación
- ✅ Vinculación a examen específico

---

### 4. Respuesta (app_examen)

```python
class Respuesta:
    pregunta = ForeignKey(Pregunta)  → RESTRICT
    contenido = TextField
    es_correcta = BooleanField
```

**Funcionalidad:**

- ✅ 3 opciones por pregunta (validar en admin)
- ✅ Solo una correcta por pregunta

---

### 5. ExamenCandidato (app_examen) ⭐ TABLA MUCHOS A MUCHOS

```python
class ExamenCandidato:
    candidato = ForeignKey(settings.AUTH_USER_MODEL)
    examen = ForeignKey(Examen)
    puntaje = DecimalField (5,2)
    fecha_presentacion = DateTimeField
    completado = BooleanField
    tiempo_empleado = DurationField

    UNIQUE_TOGETHER: (candidato, examen)
```

**Funcionalidad:**

- ✅ Relación normalizada candidato-examen
- ✅ Previene múltiples intentos (unique_together)
- ✅ Almacena puntaje y estadísticas
- ✅ Trazabilidad completa

---

### 6. RespuestaCandidato (app_examen)

```python
class RespuestaCandidato:
    examen_candidato = ForeignKey(ExamenCandidato)
    pregunta = ForeignKey(Pregunta)
    respuesta_seleccionada = ForeignKey(Respuesta)
    es_correcta = BooleanField
    fecha_respuesta = DateTimeField

    UNIQUE_TOGETHER: (examen_candidato, pregunta)
```

**Funcionalidad:**

- ✅ Detalle de cada respuesta del candidato
- ✅ Auditoría de respuestas
- ✅ Evita responder misma pregunta dos veces

---

## 🎯 Validación de Requerimientos Funcionales

### Panel Administrativo (Django Admin)

| Requerimiento                | Estado | Implementación                           |
| ---------------------------- | ------ | ---------------------------------------- |
| Gestionar banco de preguntas | ✅     | Modelos Pregunta + Respuesta             |
| 3 opciones por pregunta      | ⚠️     | Validar en admin.py con InlineModelAdmin |
| Solo 1 correcta              | ⚠️     | Validar en admin.py con clean()          |
| Crear usuarios admin         | ✅     | Modelo Administrador (AbstractUser)      |

### Módulo Administrador

| Requerimiento                 | Estado | Implementación                          |
| ----------------------------- | ------ | --------------------------------------- |
| Registrar candidatos          | ✅     | Modelo Candidato + Vista registro       |
| Enviar credenciales por email | 🔲     | Configurar EMAIL_BACKEND en settings    |
| Tabla de posiciones           | ✅     | Consulta: ExamenCandidato.objects.all() |
| Mostrar foto, cédula, puntaje | ✅     | Campos disponibles en modelo            |

### Módulo Candidato

| Requerimiento                | Estado | Implementación                         |
| ---------------------------- | ------ | -------------------------------------- |
| Realizar examen 10 preguntas | ✅     | Pregunta.objects.filter(examen=X)[:10] |
| Una sola oportunidad         | ✅     | unique_together en ExamenCandidato     |
| Mostrar puntaje previo       | ✅     | Consultar ExamenCandidato.completado   |

---

## 🔐 Seguridad y Restricciones

### Implementadas en los Modelos:

- ✅ `unique_together` en ExamenCandidato (evita reintento)
- ✅ `unique_together` en RespuestaCandidato (evita duplicados)
- ✅ `on_delete=RESTRICT` en ForeignKeys (integridad referencial)
- ✅ Campos `null=True, blank=True` apropiados

### Pendientes en Vistas:

- 🔲 Decoradores `@login_required`
- 🔲 Validación de permisos por rol
- 🔲 Restricción de URLs directas

---

## 📝 Acciones Pendientes para Admin

### app_examen/admin.py

```python
from django.contrib import admin
from django.core.exceptions import ValidationError
from .models import Examen, Pregunta, Respuesta

class RespuestaInline(admin.TabularInline):
    model = Respuesta
    extra = 3
    max_num = 3  # ✅ Limita a 3 opciones
    min_num = 3  # ✅ Requiere mínimo 3

    def save_model(self, request, obj, form, change):
        # Validar que solo haya una correcta
        pregunta = obj.pregunta
        if obj.es_correcta:
            otras_correctas = Respuesta.objects.filter(
                pregunta=pregunta,
                es_correcta=True
            ).exclude(pk=obj.pk).count()

            if otras_correctas > 0:
                raise ValidationError("Solo puede haber una respuesta correcta")
        super().save_model(request, obj, form, change)

class PreguntaAdmin(admin.ModelAdmin):
    inlines = [RespuestaInline]
    list_display = ['contenido', 'examen', 'orden']
    list_filter = ['examen']

admin.site.register(Examen)
admin.site.register(Pregunta, PreguntaAdmin)
```

---

## 🚀 Comandos para Aplicar

```bash
# 1. Instalar Pillow (requerido para ImageField)
pip install Pillow

# 2. Crear migraciones
python manage.py makemigrations app_candidatos
python manage.py makemigrations app_examen
python manage.py makemigrations app_core

# 3. Aplicar migraciones
python manage.py migrate

# 4. Crear superusuario
python manage.py createsuperuser

# 5. Crear carpetas media (opcional, se crean automáticamente)
mkdir storage
mkdir storage\candidatos
mkdir storage\preguntas

# 6. Ejecutar servidor
python manage.py runserver
```

---

## 📊 Consultas ORM Útiles

### Tabla de Posiciones (Vista Administrador)

```python
from app_examen.models import ExamenCandidato

# Candidatos con puntaje ordenados
posiciones = ExamenCandidato.objects.filter(
    completado=True
).select_related('candidato').order_by('-puntaje')

# En template:
# {{ posicion.candidato.foto.url }}
# {{ posicion.candidato.documento }}
# {{ posicion.candidato.get_full_name }}
# {{ posicion.puntaje }}
```

### Verificar si Candidato ya Presentó

```python
# En vista de examen
ya_presento = ExamenCandidato.objects.filter(
    candidato=request.user,
    examen=examen_actual,
    completado=True
).exists()

if ya_presento:
    # Mostrar mensaje con puntaje previo
    resultado = ExamenCandidato.objects.get(
        candidato=request.user,
        examen=examen_actual
    )
    return render(request, 'ya_presentado.html', {
        'puntaje': resultado.puntaje
    })
```

### Obtener 10 Preguntas Aleatorias

```python
from django.db.models import Q
import random

preguntas = list(Pregunta.objects.filter(
    examen=examen_actual
).prefetch_related('respuestas'))

# Seleccionar 10 aleatorias
preguntas_examen = random.sample(preguntas, min(10, len(preguntas)))
```

---

## ✅ Conclusión

### ✅ La base de datos cumple con:

1. ✅ Arquitectura en múltiples apps Django
2. ✅ Relación muchos a muchos normalizada (ExamenCandidato)
3. ✅ Soporte para imágenes en candidatos y preguntas
4. ✅ Estructura para 3 opciones por pregunta
5. ✅ Trazabilidad de intentos y restricción de reintento
6. ✅ Campos necesarios para tabla de posiciones
7. ✅ MEDIA_ROOT configurado como 'storage'

### ⚠️ Validaciones adicionales requeridas en:

- `admin.py`: Limitar a 3 respuestas y 1 correcta
- Vistas: Control de permisos y accesos
- Settings: Configuración de EMAIL_BACKEND

### 🎯 Próximo paso:

Ejecutar migraciones e implementar vistas con control de acceso por roles.
