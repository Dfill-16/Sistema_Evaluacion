from django.db import models
from django.conf import settings

# Create your models here.
class Examen(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True, null=True)
    
    class Meta:
        verbose_name = 'Examen'
        verbose_name_plural = 'Exámenes'
    
    def __str__(self):
        return self.nombre
    
    
class Pregunta(models.Model):
    examen = models.ForeignKey(Examen, on_delete=models.RESTRICT, related_name='preguntas')
    contenido = models.TextField(max_length=400)
    imagen = models.ImageField(upload_to='preguntas/', null=True, blank=True)
    orden = models.PositiveIntegerField(default=0)
    
    class Meta:
        verbose_name = 'Pregunta'
        verbose_name_plural = 'Preguntas'
        ordering = ['orden', 'id']
    
    def __str__(self):
        return f"Pregunta {self.id} - {self.contenido[:50]}"


class Respuesta(models.Model):
    pregunta = models.ForeignKey(Pregunta, on_delete=models.RESTRICT, related_name='respuestas')
    contenido = models.TextField(max_length=400)
    es_correcta = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'Respuesta'
        verbose_name_plural = 'Respuestas'
    
    def __str__(self):
        return f"Respuesta: {self.contenido[:30]} ({'Correcta' if self.es_correcta else 'Incorrecta'})"


class ExamenCandidato(models.Model):
    """Tabla intermedia para relación muchos a muchos entre Candidatos y Exámenes"""
    candidato = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='examenes_presentados')
    examen = models.ForeignKey(Examen, on_delete=models.CASCADE, related_name='examenes_candidatos')
    puntaje = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    fecha_presentacion = models.DateTimeField(auto_now_add=True)
    completado = models.BooleanField(default=False)
    tiempo_empleado = models.DurationField(null=True, blank=True)
    
    class Meta:
        verbose_name = '📊 Historial de Examen Presentado'
        verbose_name_plural = '📊 Historial de Exámenes Presentados'
        unique_together = ('candidato', 'examen')
    
    def __str__(self):
        return f"{self.candidato.get_full_name()} - {self.examen.nombre} - {self.puntaje}%"


class RespuestaCandidato(models.Model):
    """Almacena las respuestas de cada candidato a cada pregunta"""
    examen_candidato = models.ForeignKey(ExamenCandidato, on_delete=models.CASCADE, related_name='respuestas_dadas')
    pregunta = models.ForeignKey(Pregunta, on_delete=models.CASCADE)
    respuesta_seleccionada = models.ForeignKey(Respuesta, on_delete=models.CASCADE, null=True, blank=True)
    es_correcta = models.BooleanField(default=False)
    fecha_respuesta = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = '🔍 Auditoría de Respuesta Individual'
        verbose_name_plural = '🔍 Auditoría de Respuestas Individuales'
        unique_together = ('examen_candidato', 'pregunta')
    
    def __str__(self):
        resultado = "✅ Correcta" if self.es_correcta else "❌ Incorrecta"
        return f"{self.examen_candidato.candidato.get_full_name()} - {self.pregunta.contenido[:30]}... - {resultado}"
    
