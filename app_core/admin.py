from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin
from .models import Usuario
from .views import enviar_credenciales_email

@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'rol', 'documento', 'is_active', 'fecha_creacion']
    list_filter = ['rol', 'is_active', 'is_staff', 'is_superuser', 'fecha_creacion']
    search_fields = ['username', 'email', 'first_name', 'last_name', 'documento', 'celular']
    ordering = ['-fecha_creacion']
    
    fieldsets = (
        (None, {
            'fields': ('username', 'password')
        }),
        ('Información Personal', {
            'fields': ('first_name', 'last_name', 'email', 'documento', 'celular', 'foto')
        }),
        ('Rol y Permisos', {
            'fields': ('rol', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Fechas Importantes', {
            'fields': ('last_login', 'date_joined', 'fecha_creacion', 'fecha_modificacion'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['fecha_creacion', 'fecha_modificacion', 'last_login', 'date_joined']
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'email', 'first_name', 'last_name', 'rol', 'documento', 'celular', 'foto'),
        }),
    )

    def save_model(self, request, obj, form, change):
        raw_password = form.cleaned_data.get('password1') if not change else None
        super().save_model(request, obj, form, change)

        if not change and raw_password:
            try:
                enviado = enviar_credenciales_email(obj, obj.username, raw_password)
                if enviado:
                    self.message_user(request, 'Se enviaron las credenciales al correo del usuario.')
                else:
                    self.message_user(
                        request,
                        'Usuario creado pero no se pudo enviar el correo de credenciales. Verifica el email o la configuración SMTP.',
                        level=messages.WARNING
                    )
            except Exception as exc:
                self.message_user(
                    request,
                    f'No se enviaron las credenciales: {exc}',
                    level=messages.ERROR
                )

