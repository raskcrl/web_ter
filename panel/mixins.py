from functools import wraps

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied


def es_administrador(user):
    return bool(
        user.is_authenticated
        and user.is_active
        and user.is_staff
    )


class PanelAccessMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Permite el acceso solo a usuarios activos con is_staff=True."""

    def test_func(self):
        return es_administrador(self.request.user)


def panel_access_required(view_func):
    """Versión para vistas basadas en funciones."""

    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect_to_login(
                request.get_full_path(),
                settings.LOGIN_URL,
            )

        if not es_administrador(request.user):
            raise PermissionDenied

        return view_func(request, *args, **kwargs)

    return _wrapped
