from django.db import models

# No necesitamos modelo separado, usamos app_core.Administrador para todos los usuarios
# El modelo está en app_core con campo 'rol' para diferenciar admin/candidato