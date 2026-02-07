from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class Usuario(AbstractUser):
    """
    Modelo único de usuario para el sistema.
    Se diferencia por grupos/permisos o campo rol.
    """
    ROLES = (
        ('admin', 'Administrador'),
        ('candidato', 'Candidato'),
    )
    
    rol = models.CharField(max_length=20, choices=ROLES, default='candidato')
    documento = models.CharField(max_length=20, null=True, blank=True, unique=True)
    celular = models.CharField(max_length=20, null=True, blank=True, unique=True)
    foto = models.ImageField(upload_to='usuarios/', null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True, null=True, blank=True)
    
    # Resolver conflictos de AbstractUser
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='usuarios_core',
        blank=True,
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='usuarios_core',
        blank=True,
        verbose_name='user permissions',
    )
    
    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.get_rol_display()})"
    
    @property
    def es_administrador(self):
        return self.rol == 'admin' or self.is_superuser
    
    @property
    def es_candidato(self):
        return self.rol == 'candidato'
    
