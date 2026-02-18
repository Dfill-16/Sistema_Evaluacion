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
    list_display = ['get_candidato_nombre', 'examen', 'puntaje', 'completado', 'fecha_presentacion', 'tiempo_empleado']
    list_filter = ['completado', 'examen', 'fecha_presentacion']
    search_fields = ['candidato__username', 'candidato__email', 'candidato__first_name', 'candidato__last_name', 'examen__nombre']
    readonly_fields = ['fecha_presentacion', 'candidato', 'examen', 'puntaje', 'completado', 'tiempo_empleado']
    date_hierarchy = 'fecha_presentacion'
    
    # Permisos de solo lectura (auditoría)
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    def get_candidato_nombre(self, obj):
        return f"{obj.candidato.get_full_name()} ({obj.candidato.username})"
    get_candidato_nombre.short_description = 'Candidato'
    get_candidato_nombre.admin_order_field = 'candidato__last_name'
    
    # Cambiar el nombre en el admin
    class Meta:
        verbose_name = '📊 Historial de Exámenes Presentados'
        verbose_name_plural = '📊 Historial de Exámenes Presentados'

@admin.register(RespuestaCandidato)
class RespuestaCandidatoAdmin(admin.ModelAdmin):
    list_display = ['get_candidato_nombre', 'get_examen_nombre', 'pregunta_corta', 'respuesta_seleccionada', 'es_correcta', 'fecha_respuesta']
    list_filter = ['es_correcta', 'fecha_respuesta', 'examen_candidato__examen']
    search_fields = ['examen_candidato__candidato__username', 'examen_candidato__candidato__first_name', 'examen_candidato__candidato__last_name', 'pregunta__contenido']
    readonly_fields = ['fecha_respuesta', 'examen_candidato', 'pregunta', 'respuesta_seleccionada', 'es_correcta']
    date_hierarchy = 'fecha_respuesta'
    
    # Permisos de solo lectura (auditoría)
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    def get_candidato_nombre(self, obj):
        return f"{obj.examen_candidato.candidato.get_full_name()}"
    get_candidato_nombre.short_description = 'Candidato'
    get_candidato_nombre.admin_order_field = 'examen_candidato__candidato__last_name'
    
    def get_examen_nombre(self, obj):
        return obj.examen_candidato.examen.nombre
    get_examen_nombre.short_description = 'Examen'
    get_examen_nombre.admin_order_field = 'examen_candidato__examen__nombre'
    
    def pregunta_corta(self, obj):
        return obj.pregunta.contenido[:60] + '...' if len(obj.pregunta.contenido) > 60 else obj.pregunta.contenido
    pregunta_corta.short_description = 'Pregunta'
    
    # Cambiar el nombre en el admin
    class Meta:
        verbose_name = '🔍 Auditoría de Respuestas Detallada'
        verbose_name_plural = '🔍 Auditoría de Respuestas Detallada'
