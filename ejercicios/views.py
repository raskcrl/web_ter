from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView, ListView

from .models import Categoria, Ejercicio


class EjercicioListView(ListView):
    model = Ejercicio
    template_name = "ejercicios/ejercicio_list.html"
    context_object_name = "ejercicios"
    paginate_by = 12

    def get_queryset(self):
        queryset = (
            Ejercicio.objects.filter(activo=True, categoria__activa=True)
            .select_related("categoria")
            .order_by("categoria__orden", "categoria__nombre", "nombre")
        )

        categoria_slug = self.kwargs.get("slug")
        if categoria_slug:
            queryset = queryset.filter(categoria__slug=categoria_slug)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categorias"] = (
            Categoria.objects.filter(activa=True)
            .annotate(
                total_ejercicios=Count(
                    "ejercicios",
                    filter=Q(ejercicios__activo=True),
                )
            )
            .order_by("orden", "nombre")
        )

        categoria_slug = self.kwargs.get("slug")
        if categoria_slug:
            context["categoria_actual"] = get_object_or_404(
                Categoria,
                slug=categoria_slug,
                activa=True,
            )

        context["total_ejercicios"] = context["paginator"].count
        return context


class EjercicioDetailView(DetailView):
    model = Ejercicio
    template_name = "ejercicios/ejercicio_detail.html"
    context_object_name = "ejercicio"

    def get_queryset(self):
        return Ejercicio.objects.filter(
            activo=True,
            categoria__activa=True,
        ).select_related("categoria")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["relacionados"] = (
            Ejercicio.objects.filter(
                categoria=self.object.categoria,
                activo=True,
            )
            .exclude(pk=self.object.pk)
            .select_related("categoria")
            .order_by("nombre")[:3]
        )
        return context
