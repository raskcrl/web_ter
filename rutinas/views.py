from urllib.parse import urlencode

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Prefetch, Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.cache import never_cache
from django.views.generic import DetailView, ListView

from .models import Rutina, RutinaEjercicio, UsuarioRutina


def _redirigir_a_login(destino):
    return redirect(f"{reverse('usuarios:login')}?{urlencode({'next': destino})}")


def _destino_seguro(request, destino_predeterminado):
    destino = request.POST.get("next")

    if destino and url_has_allowed_host_and_scheme(
        destino,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return destino

    return destino_predeterminado


class RutinaListView(ListView):
    model = Rutina
    template_name = "rutinas/rutina_list.html"
    context_object_name = "rutinas"
    paginate_by = 9

    def get_queryset(self):
        return (
            Rutina.objects.filter(activa=True)
            .annotate(
                total_ejercicios=Count(
                    "rutina_ejercicios",
                    filter=Q(
                        rutina_ejercicios__ejercicio__activo=True,
                        rutina_ejercicios__ejercicio__categoria__activa=True,
                    ),
                )
            )
            .order_by("orden", "nombre")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_rutinas"] = context["paginator"].count
        return context


class RutinaDetailView(DetailView):
    model = Rutina
    template_name = "rutinas/rutina_detail.html"
    context_object_name = "rutina"

    def get_queryset(self):
        return Rutina.objects.filter(activa=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["ejercicios_rutina"] = (
            self.object.rutina_ejercicios.filter(
                ejercicio__activo=True,
                ejercicio__categoria__activa=True,
            )
            .select_related("ejercicio__categoria")
            .order_by("orden", "pk")
        )
        context["esta_guardada"] = (
            self.request.user.is_authenticated
            and UsuarioRutina.objects.filter(
                usuario=self.request.user,
                rutina=self.object,
            ).exists()
        )
        return context


@method_decorator(never_cache, name="dispatch")
class RutinaGuardadasView(LoginRequiredMixin, ListView):
    template_name = "rutinas/rutinas_guardadas.html"
    context_object_name = "rutinas_guardadas"

    def get_queryset(self):
        return (
            UsuarioRutina.objects.filter(
                usuario=self.request.user,
                rutina__activa=True,
            )
            .select_related("rutina")
            .prefetch_related(
                Prefetch(
                    "rutina__rutina_ejercicios",
                    queryset=RutinaEjercicio.objects.filter(
                        ejercicio__activo=True,
                        ejercicio__categoria__activa=True,
                    ).select_related("ejercicio__categoria"),
                    to_attr="ejercicios_visibles",
                )
            )
            .order_by("-guardado_en")
        )


def guardar_rutina(request, slug):
    destino = reverse("rutinas:detalle", args=[slug])

    if not request.user.is_authenticated:
        return _redirigir_a_login(destino)

    if request.method != "POST":
        return redirect("rutinas:detalle", slug=slug)

    rutina = get_object_or_404(Rutina, slug=slug, activa=True)
    accion = request.POST.get("accion", "guardar")

    if accion == "quitar":
        eliminadas, _ = UsuarioRutina.objects.filter(
            usuario=request.user,
            rutina=rutina,
        ).delete()

        if eliminadas:
            messages.success(
                request,
                "La rutina se quitó de tus rutinas guardadas.",
            )
        else:
            messages.info(
                request,
                "Esta rutina no estaba en tus rutinas guardadas.",
            )
    else:
        _, creada = UsuarioRutina.objects.get_or_create(
            usuario=request.user,
            rutina=rutina,
        )

        if creada:
            messages.success(
                request,
                "La rutina se guardó en tu cuenta.",
            )
        else:
            messages.info(
                request,
                "Esta rutina ya está en tus rutinas guardadas.",
            )

    return redirect(_destino_seguro(request, destino))
