from django.contrib import admin
from django.forms import BaseInlineFormSet, ValidationError as FormValidationError
import nested_admin
from .models import Examen, Pregunta, Respuesta, ExamenCandidato, RespuestaCandidato


class RespuestaFormSet(BaseInlineFormSet):
    """Valida que solo una respuesta por pregunta esté marcada como correcta."""
    def clean(self):
        super().clean()
        correctas = sum(
            1 for form in self.forms
            if form.cleaned_data.get('es_correcta') and not form.cleaned_data.get('DELETE', False)
        )
        if correctas > 1:
            raise FormValidationError('Solo puede haber una respuesta correcta por pregunta.')


class RespuestaInline(nested_admin.NestedTabularInline):
    model = Respuesta
    formset = RespuestaFormSet
    extra = 3
    max_num = 3
    min_num = 3
    can_delete = False
    fields = ['contenido', 'es_correcta']


class PreguntaInline(nested_admin.NestedStackedInline):
    model = Pregunta
    extra = 0
    max_num = 10
    can_delete = True
    fields = ['contenido', 'imagen']
    inlines = [RespuestaInline]
    show_change_link = False


@admin.register(Examen)
class ExamenAdmin(nested_admin.NestedModelAdmin):
    list_display = ['nombre', 'activo', 'fecha_creacion', 'total_preguntas']
    list_filter = ['activo']
    search_fields = ['nombre', 'descripcion']
    inlines = [PreguntaInline]

    class Media:
        js = ('js/admin_respuesta_radio.js',)

    def total_preguntas(self, obj):
        return obj.preguntas.count()
    total_preguntas.short_description = 'Total Preguntas'

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if obj.preguntas.count() > 10:
            self.message_user(
                request,
                'Este examen no puede tener más de 10 preguntas.',
                level=admin.messages.ERROR,
            )


@admin.register(ExamenCandidato)
class ExamenCandidatoAdmin(admin.ModelAdmin):
    list_display = ['get_candidato_nombre', 'examen', 'puntaje', 'completado', 'fecha_presentacion', 'tiempo_empleado']
    list_filter = ['completado', 'examen']
    search_fields = ['candidato__username', 'candidato__email', 'candidato__first_name', 'candidato__last_name', 'examen__nombre']
    readonly_fields = ['fecha_presentacion', 'candidato', 'examen', 'puntaje', 'completado', 'tiempo_empleado']
    
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
    list_filter = ['es_correcta', 'examen_candidato__examen']
    search_fields = ['examen_candidato__candidato__username', 'examen_candidato__candidato__first_name', 'examen_candidato__candidato__last_name', 'pregunta__contenido']
    readonly_fields = ['fecha_respuesta', 'examen_candidato', 'pregunta', 'respuesta_seleccionada', 'es_correcta']
    
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

