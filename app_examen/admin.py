from django.contrib import admin
from .models import Examen, Pregunta, Respuesta, ExamenCandidato, RespuestaCandidato

class RespuestaInline(admin.TabularInline):
    model = Respuesta
    extra = 3
    max_num = 3
    min_num = 3
    can_delete = True
    fields = ['contenido', 'es_correcta']

class PreguntaInline(admin.StackedInline):
    model = Pregunta
    extra = 0
    max_num = 10
    can_delete = True
    fields = ['contenido', 'imagen', 'orden']
    show_change_link = True

@admin.register(Examen)
class ExamenAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'activo', 'fecha_creacion', 'total_preguntas']
    list_filter = ['activo', 'fecha_creacion']
    search_fields = ['nombre', 'descripcion']
    inlines = [PreguntaInline]
    
    def total_preguntas(self, obj):
        return obj.preguntas.count()
    total_preguntas.short_description = 'Total Preguntas'

@admin.register(Pregunta)
class PreguntaAdmin(admin.ModelAdmin):
    list_display = ['id', 'examen', 'contenido_corto', 'orden', 'total_respuestas']
    list_filter = ['examen']
    search_fields = ['contenido']
    inlines = [RespuestaInline]
    
    def contenido_corto(self, obj):
        return obj.contenido[:50] + '...' if len(obj.contenido) > 50 else obj.contenido
    contenido_corto.short_description = 'Contenido'
    
    def total_respuestas(self, obj):
        return obj.respuestas.count()
    total_respuestas.short_description = 'Respuestas'

@admin.register(Respuesta)
class RespuestaAdmin(admin.ModelAdmin):
    list_display = ['id', 'pregunta', 'contenido_corto', 'es_correcta']
    list_filter = ['es_correcta', 'pregunta__examen']
    search_fields = ['contenido']
    
    def contenido_corto(self, obj):
        return obj.contenido[:50] + '...' if len(obj.contenido) > 50 else obj.contenido
    contenido_corto.short_description = 'Contenido'

@admin.register(ExamenCandidato)
class ExamenCandidatoAdmin(admin.ModelAdmin):
    list_display = ['candidato', 'examen', 'puntaje', 'completado', 'fecha_presentacion']
    list_filter = ['completado', 'examen', 'fecha_presentacion']
    search_fields = ['candidato__username', 'candidato__email', 'examen__nombre']
    readonly_fields = ['fecha_presentacion']

@admin.register(RespuestaCandidato)
class RespuestaCandidatoAdmin(admin.ModelAdmin):
    list_display = ['examen_candidato', 'pregunta', 'respuesta_seleccionada', 'es_correcta', 'fecha_respuesta']
    list_filter = ['es_correcta', 'fecha_respuesta']
    search_fields = ['examen_candidato__candidato__username', 'pregunta__contenido']
    readonly_fields = ['fecha_respuesta']
