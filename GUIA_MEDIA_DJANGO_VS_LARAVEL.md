# 📚 Guía: Manejo de Archivos Media en Django vs Laravel

## 🎯 Conceptos Generales

### Laravel
- **Carpeta por defecto**: `storage/app/public`
- **Link simbólico**: `php artisan storage:link` → crea enlace desde `public/storage` a `storage/app/public`
- **URL pública**: `/storage/archivo.jpg`
- **Configuración**: `config/filesystems.php`

### Django
- **Carpeta por defecto**: Configurable (en tu caso: `storage/`)
- **Configuración**: `settings.py`
- **URL pública**: `/storage/archivo.jpg` (configurable)
- **Servir archivos**: Automático en desarrollo, requiere servidor web en producción

---

## ⚙️ Configuración Settings.py (Ya aplicada)

```python
# settings.py

# Media files - Equivalente a 'storage' en Laravel
MEDIA_URL = '/storage/'  # URL pública para acceder a los archivos
MEDIA_ROOT = BASE_DIR / 'storage'  # Ruta física donde se guardan
```

### Comparación:

| Laravel | Django |
|---------|--------|
| `FILESYSTEM_DISK=public` | `MEDIA_ROOT = BASE_DIR / 'storage'` |
| `storage/app/public/` | `storage/` |
| `public/storage` (symlink) | Servido por Django automáticamente |

---

## 📂 Estructura de Carpetas

### Laravel:
```
proyecto/
├── storage/
│   ├── app/
│   │   └── public/
│   │       ├── candidatos/
│   │       └── preguntas/
│   └── framework/
└── public/
    └── storage/ → enlace simbólico
```

### Django (Tu Proyecto):
```
Sistema_Evaluacion/
├── storage/               ← Se crea automáticamente
│   ├── candidatos/       ← upload_to='candidatos/'
│   └── preguntas/        ← upload_to='preguntas/'
├── static/               ← Archivos estáticos (CSS, JS, logos)
└── staticfiles/          ← Archivos recolectados (producción)
```

---

## 🗂️ Definición en Modelos

### Laravel (Eloquent):

```php
// app/Models/Candidato.php
class Candidato extends Model
{
    protected $fillable = ['nombre', 'foto'];
    
    // Accessor para obtener la URL
    public function getFotoUrlAttribute()
    {
        return Storage::url($this->foto);
    }
}
```

**En el formulario (Blade):**
```blade
<form action="{{ route('candidatos.store') }}" method="POST" enctype="multipart/form-data">
    @csrf
    <input type="file" name="foto">
</form>
```

**En el controlador:**
```php
$path = $request->file('foto')->store('candidatos', 'public');
$candidato->foto = $path; // guarda: candidatos/nombrearchivo.jpg
```

### Django (ORM):

```python
# app_candidatos/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser

class Candidato(AbstractUser):
    foto = models.ImageField(upload_to='candidatos/', null=True, blank=True)
    # upload_to define la subcarpeta dentro de MEDIA_ROOT
    # Se guardará en: storage/candidatos/nombrearchivo.jpg
```

**En el formulario (Template):**
```html
<form action="{% url 'crear_candidato' %}" method="POST" enctype="multipart/form-data">
    {% csrf_token %}
    <input type="file" name="foto">
</form>
```

**En la vista:**
```python
from django.core.files.storage import default_storage

def crear_candidato(request):
    if request.method == 'POST' and request.FILES.get('foto'):
        foto = request.FILES['foto']
        candidato = Candidato.objects.create(
            username=request.POST['username'],
            foto=foto  # Django maneja automáticamente el guardado
        )
```

---

## 🖼️ Mostrar Imágenes en Templates

### Laravel (Blade):

```blade
@if($candidato->foto)
    <img src="{{ Storage::url($candidato->foto) }}" alt="Foto">
    <!-- O usando accessor -->
    <img src="{{ $candidato->foto_url }}" alt="Foto">
@endif
```

### Django (Templates):

```django
{% if candidato.foto %}
    <img src="{{ candidato.foto.url }}" alt="Foto">
{% endif %}

<!-- Verificar si existe archivo -->
{% if candidato.foto and candidato.foto.name %}
    <img src="{{ candidato.foto.url }}" alt="Foto">
{% else %}
    <img src="{% static 'img/default-avatar.png' %}" alt="Sin foto">
{% endif %}
```

---

## 🔧 Operaciones Comunes

### 1. Guardar Archivo

**Laravel:**
```php
// Guardar con nombre automático
$path = $request->file('foto')->store('candidatos', 'public');

// Guardar con nombre personalizado
$nombre = 'candidato_' . time() . '.' . $extension;
$path = $request->file('foto')->storeAs('candidatos', $nombre, 'public');
```

**Django:**
```python
# Guardar automáticamente (en el save del modelo)
candidato.foto = request.FILES['foto']
candidato.save()

# Guardar con nombre personalizado
from django.core.files.base import ContentFile
import uuid

def handle_uploaded_file(f):
    extension = f.name.split('.')[-1]
    filename = f'candidato_{uuid.uuid4()}.{extension}'
    candidato.foto.save(filename, ContentFile(f.read()))
```

### 2. Eliminar Archivo

**Laravel:**
```php
use Illuminate\Support\Facades\Storage;

Storage::disk('public')->delete($candidato->foto);
```

**Django:**
```python
import os

# Opción 1: Eliminar archivo físico
if candidato.foto:
    candidato.foto.delete(save=False)  # save=False evita guardar el modelo

# Opción 2: Eliminar manualmente
if candidato.foto:
    os.remove(candidato.foto.path)
    candidato.foto = None
    candidato.save()
```

### 3. Verificar si existe

**Laravel:**
```php
if (Storage::disk('public')->exists($candidato->foto)) {
    // Archivo existe
}
```

**Django:**
```python
from django.core.files.storage import default_storage

if candidato.foto and default_storage.exists(candidato.foto.name):
    # Archivo existe
    
# O más simple:
if candidato.foto and candidato.foto.name:
    # Archivo existe
```

### 4. Obtener URL completa

**Laravel:**
```php
$url = Storage::url($candidato->foto);
// Resultado: /storage/candidatos/foto.jpg
```

**Django:**
```python
url = candidato.foto.url if candidato.foto else None
# Resultado: /storage/candidatos/foto.jpg

# URL absoluta (con dominio)
from django.contrib.sites.shortcuts import get_current_site
full_url = request.build_absolute_uri(candidato.foto.url)
# Resultado: http://localhost:8000/storage/candidatos/foto.jpg
```

---

## 🛠️ Configuración en Producción

### Laravel:
```bash
# Crear enlace simbólico
php artisan storage:link

# Configurar permisos
chmod -R 775 storage/
chown -R www-data:www-data storage/
```

**Nginx:**
```nginx
location /storage {
    alias /path/to/proyecto/storage/app/public;
}
```

### Django:
```python
# settings.py (producción)
STATIC_ROOT = '/var/www/proyecto/static/'
MEDIA_ROOT = '/var/www/proyecto/storage/'
```

**Nginx:**
```nginx
location /storage/ {
    alias /var/www/proyecto/storage/;
}

location /static/ {
    alias /var/www/proyecto/static/;
}
```

---

## 📋 Validaciones

### Laravel (FormRequest):
```php
public function rules()
{
    return [
        'foto' => 'required|image|mimes:jpeg,png,jpg|max:2048',
    ];
}
```

### Django (Forms):
```python
from django import forms

class CandidatoForm(forms.ModelForm):
    class Meta:
        model = Candidato
        fields = ['username', 'foto']
    
    def clean_foto(self):
        foto = self.cleaned_data.get('foto')
        if foto:
            if foto.size > 2 * 1024 * 1024:  # 2MB
                raise forms.ValidationError("El archivo no debe superar 2MB")
            if not foto.content_type in ['image/jpeg', 'image/png', 'image/jpg']:
                raise forms.ValidationError("Solo se permiten imágenes JPEG o PNG")
        return foto
```

---

## 🎓 Resumen de Equivalencias

| Concepto | Laravel | Django |
|----------|---------|--------|
| **Configuración** | `config/filesystems.php` | `settings.MEDIA_ROOT` |
| **Subcarpeta** | `store('candidatos')` | `upload_to='candidatos/'` |
| **URL pública** | `Storage::url()` | `objeto.foto.url` |
| **Ruta física** | `Storage::path()` | `objeto.foto.path` |
| **Guardar** | `store()` / `storeAs()` | `modelo.save()` |
| **Eliminar** | `Storage::delete()` | `objeto.foto.delete()` |
| **Enlace público** | `php artisan storage:link` | Automático en desarrollo |

---

## ✅ Checklist de Implementación

- [x] Configurar `MEDIA_URL` y `MEDIA_ROOT` en `settings.py`
- [x] Agregar campo `ImageField` en los modelos
- [x] Configurar URLs para servir archivos media en desarrollo
- [ ] Crear carpeta `storage/` en el proyecto (se crea automáticamente)
- [ ] Instalar Pillow: `pip install Pillow` (requerido para ImageField)
- [ ] Hacer migraciones: `python manage.py makemigrations`
- [ ] Aplicar migraciones: `python manage.py migrate`
- [ ] Probar subida de archivos
- [ ] Configurar servidor web en producción (Nginx/Apache)

---

## 🚀 Próximos Pasos

1. **Instalar Pillow** (requerido para manejo de imágenes):
   ```bash
   pip install Pillow
   ```

2. **Crear migraciones**:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

3. **Probar en el admin de Django**:
   - Registrar los modelos en `admin.py`
   - Subir una imagen de prueba
   - Verificar que se cree en `storage/candidatos/` o `storage/preguntas/`

4. **Crear formularios** en tus vistas para la carga de archivos

---

## 📧 Ejemplo Completo: Registro de Candidato con Foto

### Vista:
```python
from django.shortcuts import render, redirect
from .models import Candidato

def registrar_candidato(request):
    if request.method == 'POST':
        candidato = Candidato(
            username=request.POST['username'],
            email=request.POST['email'],
            documento=request.POST['documento'],
            telefono=request.POST['telefono'],
        )
        
        if request.FILES.get('foto'):
            candidato.foto = request.FILES['foto']
        
        candidato.set_password(request.POST['password'])
        candidato.save()
        
        return redirect('lista_candidatos')
    
    return render(request, 'candidatos/registro.html')
```

### Template:
```html
<form method="POST" enctype="multipart/form-data">
    {% csrf_token %}
    <input type="text" name="username" required>
    <input type="email" name="email" required>
    <input type="text" name="documento" required>
    <input type="file" name="foto" accept="image/*">
    <input type="password" name="password" required>
    <button type="submit">Registrar</button>
</form>
```

---

¡Configuración completa! Ahora tu proyecto Django maneja archivos media de forma similar a Laravel. 🎉
