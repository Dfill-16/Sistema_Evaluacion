from django.conf import settings
from django.core.cache import cache
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse


class RateLimitMiddleware:
    """
    Middleware simple de rate limiting por IP y path.
    Usa cache por defecto; configurable con RATE_LIMIT_REQUESTS y RATE_LIMIT_WINDOW (segundos).
    Excluye rutas estáticas/media y rutas indicadas en RATE_LIMIT_EXEMPT_PATHS.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.limit = getattr(settings, "RATE_LIMIT_REQUESTS", 100)
        self.window = getattr(settings, "RATE_LIMIT_WINDOW", 60)
        self.exempt_paths = set(getattr(settings, "RATE_LIMIT_EXEMPT_PATHS", []))

    def __call__(self, request):
        if not self._should_check(request):
            return self.get_response(request)

        key = self._build_key(request)
        cache.add(key, 0, self.window)
        try:
            count = cache.incr(key)
        except ValueError:
            cache.set(key, 1, self.window)
            count = 1

        if count > self.limit:
            retry_after = max(1, int(self.window))
            return HttpResponse("Too many requests", status=429, headers={"Retry-After": str(retry_after)})

        return self.get_response(request)

    def _should_check(self, request):
        path = request.path or "/"

        if path.startswith(getattr(settings, "STATIC_URL", "/static/")):
            return False
        if path.startswith(getattr(settings, "MEDIA_URL", "/media/")) or path.startswith("/storage/"):
            return False
        if any(path.startswith(p) for p in self.exempt_paths):
            return False

        return True

    def _build_key(self, request):
        ip = request.META.get("REMOTE_ADDR", "unknown")
        path = request.path or "/"
        return f"rl:{ip}:{path}"


class RedirectToDashboardMiddleware:
    """
    Redirige cualquier respuesta 404 al dashboard principal correspondiente.
    - Anónimo → login
    - Superusuario → admin index
    - Administrador → dashboard administrador
    - Candidato → dashboard candidato
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if response.status_code != 404:
            return response

        target_path = self._resolve_target_path(request)
        if not target_path or request.path == target_path:
            return response

        return redirect(target_path)

    def _resolve_target_path(self, request):
        user = getattr(request, "user", None)

        if not user or not user.is_authenticated:
            return settings.LOGIN_URL or "/login/"

        if user.is_superuser:
            return reverse("admin:index")

        if getattr(user, "es_administrador", False):
            return reverse("app_core:dashboard_administrador")

        if getattr(user, "es_candidato", False):
            return reverse("app_candidatos:dashboard_candidato")

        return settings.LOGIN_REDIRECT_URL or "/"
