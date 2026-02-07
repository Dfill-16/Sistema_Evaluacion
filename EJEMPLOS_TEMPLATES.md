# 🖼️ Ejemplos Prácticos de Uso de Imágenes en Templates

## 📁 Estructura de Archivos

```
Sistema_Evaluacion/
├── storage/                    ← MEDIA_ROOT (archivos subidos)
│   ├── usuarios/
│   │   ├── usuario_123.jpg
│   │   └── usuario_456.png
│   └── preguntas/
│       ├── pregunta_1.jpg
│       └── pregunta_2.png
├── static/                     ← STATIC (archivos del proyecto)
│   ├── css/
│   │   └── estilos.css
│   ├── js/
│   │   └── scripts.js
│   └── img/
│       ├── logo.png           ← Logo empresa
│       └── default-avatar.png ← Avatar por defecto
└── staticfiles/               ← Archivos recolectados (producción)
```

---

## 1️⃣ Tabla de Posiciones (Vista Administrador)

### Template: `templates/admin/tabla_posiciones.html`

```html
{% load static %}
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tabla de Posiciones</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="{% static 'css/estilos.css' %}">
</head>
<body>
    <div class="container mt-5">
        <!-- Logo de la empresa (STATIC) -->
        <div class="text-center mb-4">
            <img src="{% static 'img/logo.png' %}" alt="Logo Empresa" class="logo" style="max-width: 200px;">
            <h2 class="mt-3">Tabla de Posiciones</h2>
        </div>

        <div class="table-responsive">
            <table class="table table-striped table-hover">
                <thead class="table-dark">
                    <tr>
                        <th>Posición</th>
                        <th>Foto</th>
                        <th>Cédula</th>
                        <th>Nombre Completo</th>
                        <th>Correo</th>
                        <th>Puntaje</th>
                        <th>Examen</th>
                        <th>Fecha</th>
                    </tr>
                </thead>
                <tbody>
                    {% for posicion in posiciones %}
                    <tr>
                        <td>{{ forloop.counter }}</td>
                        
                        <!-- Foto del candidato (MEDIA) -->
                        <td>
                            {% if posicion.candidato.foto and posicion.candidato.foto.name %}
                                <img src="{{ posicion.candidato.foto.url }}" 
                                     alt="Foto {{ posicion.candidato.get_full_name }}" 
                                     class="rounded-circle" 
                                     style="width: 50px; height: 50px; object-fit: cover;">
                            {% else %}
                                <img src="{% static 'img/default-avatar.png' %}" 
                                     alt="Sin foto" 
                                     class="rounded-circle" 
                                     style="width: 50px; height: 50px; object-fit: cover;">
                            {% endif %}
                        </td>
                        
                        <td>{{ posicion.candidato.documento }}</td>
                        <td>{{ posicion.candidato.get_full_name }}</td>
                        <td>{{ posicion.candidato.email }}</td>
                        <td>
                            <span class="badge bg-primary fs-6">{{ posicion.puntaje }}</span>
                        </td>
                        <td>{{ posicion.examen.nombre }}</td>
                        <td>{{ posicion.fecha_presentacion|date:"d/m/Y H:i" }}</td>
                    </tr>
                    {% empty %}
                    <tr>
                        <td colspan="8" class="text-center">No hay resultados disponibles</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
```

---

## 2️⃣ Formulario de Registro de Candidato

### Template: `templates/admin/registrar_candidato.html`

```html
{% load static %}
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Registrar Candidato</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <div class="container mt-5">
        <div class="row justify-content-center">
            <div class="col-md-8">
                <div class="card shadow">
                    <div class="card-header bg-primary text-white">
                        <h4 class="mb-0">Registrar Nuevo Candidato</h4>
                    </div>
                    <div class="card-body">
                        <!-- IMPORTANTE: enctype="multipart/form-data" para subir archivos -->
                        <form method="POST" enctype="multipart/form-data">
                            {% csrf_token %}
                            
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label for="first_name" class="form-label">Nombres *</label>
                                    <input type="text" class="form-control" id="first_name" name="first_name" required>
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label for="last_name" class="form-label">Apellidos *</label>
                                    <input type="text" class="form-control" id="last_name" name="last_name" required>
                                </div>
                            </div>

                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label for="documento" class="form-label">Cédula *</label>
                                    <input type="text" class="form-control" id="documento" name="documento" required>
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label for="celular" class="form-label">Celular</label>
                                    <input type="text" class="form-control" id="celular" name="celular">
                                </div>
                            </div>

                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label for="email" class="form-label">Correo Electrónico *</label>
                                    <input type="email" class="form-control" id="email" name="email" required>
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label for="username" class="form-label">Usuario *</label>
                                    <input type="text" class="form-control" id="username" name="username" required>
                                </div>
                            </div>

                            <!-- Campo para subir foto -->
                            <div class="mb-3">
                                <label for="foto" class="form-label">Foto del Candidato</label>
                                <input type="file" class="form-control" id="foto" name="foto" 
                                       accept="image/jpeg,image/png,image/jpg">
                                <small class="text-muted">Formatos permitidos: JPG, PNG (máx. 2MB)</small>
                            </div>

                            <!-- Vista previa de imagen -->
                            <div class="mb-3">
                                <img id="preview" src="#" alt="Vista previa" 
                                     style="display: none; max-width: 200px; margin-top: 10px;" 
                                     class="img-thumbnail">
                            </div>

                            <div class="d-grid gap-2">
                                <button type="submit" class="btn btn-primary">Registrar Candidato</button>
                                <a href="{% url 'tabla_posiciones' %}" class="btn btn-secondary">Cancelar</a>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Script para vista previa de imagen -->
    <script>
        document.getElementById('foto').addEventListener('change', function(e) {
            const file = e.target.files[0];
            const preview = document.getElementById('preview');
            
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    preview.src = e.target.result;
                    preview.style.display = 'block';
                }
                reader.readAsDataURL(file);
            } else {
                preview.style.display = 'none';
            }
        });
    </script>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
```

---

## 3️⃣ Vista de Examen (Candidato)

### Template: `templates/candidato/examen.html`

```html
{% load static %}
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Examen - {{ examen.nombre }}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        .pregunta-imagen {
            max-width: 100%;
            height: auto;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            margin: 15px 0;
        }
        .pregunta-card {
            transition: transform 0.2s;
        }
        .pregunta-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }
    </style>
</head>
<body>
    <div class="container mt-5">
        <div class="text-center mb-4">
            <h2>{{ examen.nombre }}</h2>
            <p class="text-muted">{{ examen.descripcion }}</p>
        </div>

        <form method="POST" id="form-examen">
            {% csrf_token %}
            
            {% for pregunta in preguntas %}
            <div class="card pregunta-card mb-4">
                <div class="card-header bg-info text-white">
                    <h5 class="mb-0">Pregunta {{ forloop.counter }} de {{ preguntas|length }}</h5>
                </div>
                <div class="card-body">
                    <!-- Contenido de la pregunta -->
                    <p class="lead">{{ pregunta.contenido }}</p>
                    
                    <!-- Imagen de la pregunta (MEDIA) si existe -->
                    {% if pregunta.imagen and pregunta.imagen.name %}
                    <div class="text-center">
                        <img src="{{ pregunta.imagen.url }}" 
                             alt="Imagen pregunta {{ forloop.counter }}" 
                             class="pregunta-imagen">
                    </div>
                    {% endif %}
                    
                    <!-- Opciones de respuesta -->
                    <div class="mt-3">
                        {% for respuesta in pregunta.respuestas.all %}
                        <div class="form-check mb-2">
                            <input class="form-check-input" 
                                   type="radio" 
                                   name="pregunta_{{ pregunta.id }}" 
                                   id="respuesta_{{ respuesta.id }}"
                                   value="{{ respuesta.id }}"
                                   required>
                            <label class="form-check-label" for="respuesta_{{ respuesta.id }}">
                                {{ respuesta.contenido }}
                            </label>
                        </div>
                        {% endfor %}
                    </div>
                </div>
            </div>
            {% endfor %}
            
            <div class="text-center mb-5">
                <button type="submit" class="btn btn-success btn-lg">
                    Finalizar y Enviar Examen
                </button>
            </div>
        </form>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    
    <!-- Confirmación antes de enviar -->
    <script>
        document.getElementById('form-examen').addEventListener('submit', function(e) {
            const confirmacion = confirm('¿Estás seguro de enviar el examen? No podrás volver a presentarlo.');
            if (!confirmacion) {
                e.preventDefault();
            }
        });
    </script>
</body>
</html>
```

---

## 4️⃣ Vista de Resultado (Ya Presentó)

### Template: `templates/candidato/ya_presento.html`

```html
{% load static %}
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Resultado del Examen</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <div class="container mt-5">
        <div class="row justify-content-center">
            <div class="col-md-6">
                <div class="card shadow">
                    <div class="card-header bg-warning text-dark text-center">
                        <h4>⚠️ Examen Ya Presentado</h4>
                    </div>
                    <div class="card-body text-center">
                        <!-- Foto del candidato -->
                        {% if user.foto and user.foto.name %}
                        <img src="{{ user.foto.url }}" 
                             alt="Foto {{ user.get_full_name }}" 
                             class="rounded-circle mb-3" 
                             style="width: 120px; height: 120px; object-fit: cover;">
                        {% else %}
                        <img src="{% static 'img/default-avatar.png' %}" 
                             alt="Sin foto" 
                             class="rounded-circle mb-3" 
                             style="width: 120px; height: 120px; object-fit: cover;">
                        {% endif %}
                        
                        <h5>{{ user.get_full_name }}</h5>
                        <p class="text-muted">{{ user.documento }}</p>
                        
                        <hr>
                        
                        <p class="lead">Ya has presentado este examen anteriormente.</p>
                        <p>No puedes volver a realizarlo.</p>
                        
                        <div class="alert alert-info mt-3">
                            <h3 class="mb-0">Tu Puntaje: <strong>{{ puntaje }}</strong></h3>
                            <small class="text-muted">Fecha: {{ fecha|date:"d/m/Y H:i" }}</small>
                        </div>
                        
                        <a href="{% url 'dashboard_candidato' %}" class="btn btn-primary mt-3">
                            Volver al Inicio
                        </a>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
```

---

## 5️⃣ Perfil de Usuario (Editar Foto)

### Template: `templates/perfil/editar.html`

```html
{% load static %}
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Editar Perfil</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <div class="container mt-5">
        <div class="row justify-content-center">
            <div class="col-md-8">
                <div class="card">
                    <div class="card-header">
                        <h4>Editar Perfil</h4>
                    </div>
                    <div class="card-body">
                        <form method="POST" enctype="multipart/form-data">
                            {% csrf_token %}
                            
                            <div class="text-center mb-4">
                                <!-- Foto actual -->
                                {% if user.foto and user.foto.name %}
                                <img src="{{ user.foto.url }}" 
                                     id="foto-actual" 
                                     alt="Foto actual" 
                                     class="rounded-circle mb-3" 
                                     style="width: 150px; height: 150px; object-fit: cover;">
                                {% else %}
                                <img src="{% static 'img/default-avatar.png' %}" 
                                     id="foto-actual" 
                                     alt="Sin foto" 
                                     class="rounded-circle mb-3" 
                                     style="width: 150px; height: 150px; object-fit: cover;">
                                {% endif %}
                            </div>
                            
                            <div class="mb-3">
                                <label for="foto" class="form-label">Cambiar Foto</label>
                                <input type="file" class="form-control" id="foto" name="foto" 
                                       accept="image/jpeg,image/png,image/jpg">
                            </div>
                            
                            {% if user.foto and user.foto.name %}
                            <div class="form-check mb-3">
                                <input class="form-check-input" type="checkbox" id="eliminar_foto" name="eliminar_foto">
                                <label class="form-check-label" for="eliminar_foto">
                                    Eliminar foto actual
                                </label>
                            </div>
                            {% endif %}
                            
                            <hr>
                            
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label for="first_name" class="form-label">Nombres</label>
                                    <input type="text" class="form-control" id="first_name" name="first_name" 
                                           value="{{ user.first_name }}">
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label for="last_name" class="form-label">Apellidos</label>
                                    <input type="text" class="form-control" id="last_name" name="last_name" 
                                           value="{{ user.last_name }}">
                                </div>
                            </div>
                            
                            <div class="mb-3">
                                <label for="celular" class="form-label">Celular</label>
                                <input type="text" class="form-control" id="celular" name="celular" 
                                       value="{{ user.celular|default:'' }}">
                            </div>
                            
                            <button type="submit" class="btn btn-primary">Guardar Cambios</button>
                            <a href="{% url 'dashboard_candidato' %}" class="btn btn-secondary">Cancelar</a>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        // Vista previa al cambiar foto
        document.getElementById('foto').addEventListener('change', function(e) {
            const file = e.target.files[0];
            const preview = document.getElementById('foto-actual');
            
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    preview.src = e.target.result;
                }
                reader.readAsDataURL(file);
            }
        });
    </script>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
```

---

## 🔑 Conceptos Clave en Templates

### 1. Archivos STATIC vs MEDIA

```django
{# STATIC: Archivos del proyecto (logo, CSS, JS) #}
{% load static %}
<img src="{% static 'img/logo.png' %}" alt="Logo">
<link rel="stylesheet" href="{% static 'css/estilos.css' %}">

{# MEDIA: Archivos subidos por usuarios (fotos, imágenes de preguntas) #}
{% if usuario.foto %}
    <img src="{{ usuario.foto.url }}" alt="Foto">
{% endif %}
```

### 2. Verificar si existe imagen antes de mostrar

```django
{# Opción 1: Verificar con and #}
{% if candidato.foto and candidato.foto.name %}
    <img src="{{ candidato.foto.url }}" alt="Foto">
{% else %}
    <img src="{% static 'img/default-avatar.png' %}" alt="Sin foto">
{% endif %}

{# Opción 2: Solo verificar objeto #}
{% if pregunta.imagen %}
    <img src="{{ pregunta.imagen.url }}" alt="Imagen pregunta">
{% endif %}
```

### 3. Formularios con archivos

```html
<!-- SIEMPRE agregar enctype="multipart/form-data" -->
<form method="POST" enctype="multipart/form-data">
    {% csrf_token %}
    <input type="file" name="foto" accept="image/*">
</form>
```

### 4. URLs de imágenes

```django
{# URL relativa #}
{{ usuario.foto.url }}
{# Resultado: /storage/usuarios/foto.jpg #}

{# URL absoluta (con dominio) #}
{{ request.build_absolute_uri }}{{ usuario.foto.url }}
{# Resultado: http://localhost:8000/storage/usuarios/foto.jpg #}

{# Path físico (solo en Python, no en templates) #}
{# usuario.foto.path → D:\...\storage\usuarios\foto.jpg #}
```

---

## ✅ Checklist de Uso en Templates

- [x] Usar `{% load static %}` al inicio del template
- [x] Archivos estáticos con `{% static 'ruta' %}`
- [x] Archivos media con `{{ objeto.campo.url }}`
- [x] Siempre verificar existencia: `{% if objeto.campo and objeto.campo.name %}`
- [x] Formularios con `enctype="multipart/form-data"`
- [x] Vista previa con JavaScript (opcional)
- [x] Imagen por defecto cuando no existe foto
- [x] Responsive con Bootstrap classes (`img-fluid`, `rounded-circle`)

---

## 🎨 CSS Personalizado (opcional)

### `static/css/estilos.css`

```css
/* Logo */
.logo {
    max-height: 80px;
    width: auto;
}

/* Avatares */
.avatar-sm {
    width: 40px;
    height: 40px;
    object-fit: cover;
}

.avatar-md {
    width: 80px;
    height: 80px;
    object-fit: cover;
}

.avatar-lg {
    width: 150px;
    height: 150px;
    object-fit: cover;
}

/* Imágenes de preguntas */
.pregunta-imagen {
    max-width: 600px;
    height: auto;
    border: 2px solid #dee2e6;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

/* Tabla responsive */
.table-responsive {
    box-shadow: 0 0 20px rgba(0,0,0,0.1);
    border-radius: 8px;
    overflow: hidden;
}

/* Cards */
.card {
    border: none;
    border-radius: 10px;
    transition: all 0.3s ease;
}

.card:hover {
    box-shadow: 0 5px 15px rgba(0,0,0,0.2);
}
```

---

¡Ahora tienes todos los ejemplos para implementar las vistas con imágenes! 🎉
