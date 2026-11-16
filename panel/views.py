from django.contrib import messages
from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from django.db.models.deletion import ProtectedError
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from django.views.generic import TemplateView

from ejercicios.models import Categoria, Ejercicio
from rutinas.models import Rutina, RutinaEjercicio

from .forms import (
    CategoriaForm,
    EjercicioForm,
    RutinaEjercicioForm,
    RutinaForm,
)
from .mixins import PanelAccessMixin, panel_access_required

User = get_user_model()


class DashboardView(PanelAccessMixin, TemplateView):
    template_name = "panel/dashboard.html"
    extra_context = {"panel_section": "dashboard"}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "total_categorias": Categoria.objects.count(),
                "categorias_activas": Categoria.objects.filter(activa=True).count(),
                "total_ejercicios": Ejercicio.objects.count(),
                "ejercicios_activos": Ejercicio.objects.filter(activo=True).count(),
                "total_rutinas": Rutina.objects.count(),
                "rutinas_activas": Rutina.objects.filter(activa=True).count(),
                "total_usuarios": User.objects.count(),
                "usuarios_activos": User.objects.filter(is_active=True).count(),
                "total_staff": User.objects.filter(
                    is_active=True,
                    is_staff=True,
                ).count(),
                "ultimos_ejercicios": (
                    Ejercicio.objects.select_related("categoria")
                    .order_by("-creado")[:5]
                ),
                "ultimas_rutinas": Rutina.objects.order_by("-creado")[:5],
            }
        )
        return context


@panel_access_required
def categorias_lista(request):
    categorias = Categoria.objects.annotate(
        total_ejercicios=Count("ejercicios")
    ).order_by("orden", "nombre")

    consulta = request.GET.get("q", "").strip()
    if consulta:
        categorias = categorias.filter(
            Q(nombre__icontains=consulta)
            | Q(descripcion__icontains=consulta)
        )

    return render(
        request,
        "panel/categorias_lista.html",
        {
            "panel_section": "categorias",
            "categorias": categorias,
            "consulta": consulta,
        },
    )


@panel_access_required
def categoria_crear(request):
    if request.method == "POST":
        form = CategoriaForm(request.POST)

        if form.is_valid():
            categoria = form.save()
            messages.success(
                request,
                f"La categoría «{categoria.nombre}» se creó correctamente.",
            )
            return redirect("panel:categorias")
    else:
        form = CategoriaForm()

    return render(
        request,
        "panel/categoria_form.html",
        {
            "panel_section": "categorias",
            "form": form,
            "titulo": "Nueva categoría",
            "descripcion": "Crea una categoría para organizar el catálogo.",
            "url_cancelar": "panel:categorias",
        },
    )


@panel_access_required
def categoria_editar(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)

    if request.method == "POST":
        form = CategoriaForm(request.POST, instance=categoria)

        if form.is_valid():
            categoria = form.save()
            messages.success(
                request,
                f"La categoría «{categoria.nombre}» se actualizó correctamente.",
            )
            return redirect("panel:categorias")
    else:
        form = CategoriaForm(instance=categoria)

    return render(
        request,
        "panel/categoria_form.html",
        {
            "panel_section": "categorias",
            "form": form,
            "categoria": categoria,
            "titulo": "Editar categoría",
            "descripcion": f"Actualiza los datos de «{categoria.nombre}».",
            "url_cancelar": "panel:categorias",
        },
    )


@panel_access_required
def categoria_eliminar(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)
    total_ejercicios = categoria.ejercicios.count()
    puede_eliminar = total_ejercicios == 0

    if request.method == "POST":
        if not puede_eliminar:
            messages.error(
                request,
                "No se puede eliminar la categoría porque tiene ejercicios asociados.",
            )
            return redirect("panel:categorias")

        nombre = categoria.nombre
        try:
            categoria.delete()
        except ProtectedError:
            messages.error(
                request,
                "No se puede eliminar la categoría porque tiene registros asociados.",
            )
        else:
            messages.success(
                request,
                f"La categoría «{nombre}» se eliminó correctamente.",
            )

        return redirect("panel:categorias")

    dependencias = [
        f"{total_ejercicios} ejercicio(s) asociado(s)"
    ] if total_ejercicios else []

    return render(
        request,
        "panel/confirmar_accion.html",
        {
            "panel_section": "categorias",
            "titulo": "Eliminar categoría",
            "mensaje": (
                f"¿Seguro que deseas eliminar la categoría «{categoria.nombre}»?"
            ),
            "objeto": categoria,
            "dependencias": dependencias,
            "puede_confirmar": puede_eliminar,
            "texto_confirmar": "Eliminar categoría",
            "url_cancelar": "panel:categorias",
        },
    )


@panel_access_required
def ejercicios_lista(request):
    ejercicios = (
        Ejercicio.objects.select_related("categoria")
        .annotate(total_rutinas=Count("asociaciones_rutina"))
        .order_by("categoria__orden", "categoria__nombre", "nombre")
    )

    consulta = request.GET.get("q", "").strip()
    if consulta:
        ejercicios = ejercicios.filter(
            Q(nombre__icontains=consulta)
            | Q(descripcion__icontains=consulta)
            | Q(instrucciones__icontains=consulta)
            | Q(categoria__nombre__icontains=consulta)
        )

    categoria_id = request.GET.get("categoria", "").strip()
    if categoria_id.isdigit():
        ejercicios = ejercicios.filter(categoria_id=categoria_id)
    else:
        categoria_id = ""

    return render(
        request,
        "panel/ejercicios_lista.html",
        {
            "panel_section": "ejercicios",
            "ejercicios": ejercicios,
            "categorias": Categoria.objects.order_by("orden", "nombre"),
            "consulta": consulta,
            "categoria_id": categoria_id,
        },
    )


@panel_access_required
def ejercicio_crear(request):
    if request.method == "POST":
        form = EjercicioForm(request.POST, request.FILES)

        if form.is_valid():
            ejercicio = form.save()
            messages.success(
                request,
                f"El ejercicio «{ejercicio.nombre}» se creó correctamente.",
            )
            return redirect("panel:ejercicios")
    else:
        form = EjercicioForm()

    return render(
        request,
        "panel/ejercicio_form.html",
        {
            "panel_section": "ejercicios",
            "form": form,
            "titulo": "Nuevo ejercicio",
            "descripcion": "Registra un ejercicio y asígnalo a una categoría.",
            "url_cancelar": "panel:ejercicios",
        },
    )


@panel_access_required
def ejercicio_editar(request, pk):
    ejercicio = get_object_or_404(
        Ejercicio.objects.select_related("categoria"),
        pk=pk,
    )

    if request.method == "POST":
        form = EjercicioForm(request.POST, request.FILES, instance=ejercicio)

        if form.is_valid():
            ejercicio = form.save()
            messages.success(
                request,
                f"El ejercicio «{ejercicio.nombre}» se actualizó correctamente.",
            )
            return redirect("panel:ejercicios")
    else:
        form = EjercicioForm(instance=ejercicio)

    return render(
        request,
        "panel/ejercicio_form.html",
        {
            "panel_section": "ejercicios",
            "form": form,
            "ejercicio": ejercicio,
            "titulo": "Editar ejercicio",
            "descripcion": f"Actualiza los datos de «{ejercicio.nombre}».",
            "url_cancelar": "panel:ejercicios",
        },
    )


@panel_access_required
def ejercicio_eliminar(request, pk):
    ejercicio = get_object_or_404(
        Ejercicio.objects.select_related("categoria"),
        pk=pk,
    )
    asociaciones = ejercicio.asociaciones_rutina.select_related("rutina")
    total_rutinas = asociaciones.count()
    puede_eliminar = total_rutinas == 0

    if request.method == "POST":
        if not puede_eliminar:
            messages.error(
                request,
                "No se puede eliminar el ejercicio porque forma parte de una rutina.",
            )
            return redirect("panel:ejercicios")

        nombre = ejercicio.nombre
        try:
            ejercicio.delete()
        except ProtectedError:
            messages.error(
                request,
                "No se puede eliminar el ejercicio porque tiene registros asociados.",
            )
        else:
            messages.success(
                request,
                f"El ejercicio «{nombre}» se eliminó correctamente.",
            )

        return redirect("panel:ejercicios")

    dependencias = []
    if total_rutinas:
        nombres = ", ".join(
            asociacion.rutina.nombre for asociacion in asociaciones
        )
        dependencias.append(f"Rutinas: {nombres}")

    return render(
        request,
        "panel/confirmar_accion.html",
        {
            "panel_section": "ejercicios",
            "titulo": "Eliminar ejercicio",
            "mensaje": (
                f"¿Seguro que deseas eliminar el ejercicio «{ejercicio.nombre}»?"
            ),
            "objeto": ejercicio,
            "dependencias": dependencias,
            "puede_confirmar": puede_eliminar,
            "texto_confirmar": "Eliminar ejercicio",
            "url_cancelar": "panel:ejercicios",
        },
    )


@panel_access_required
def rutinas_lista(request):
    rutinas = (
        Rutina.objects.annotate(
            total_ejercicios=Count("rutina_ejercicios")
        ).order_by("orden", "nombre")
    )

    consulta = request.GET.get("q", "").strip()
    if consulta:
        rutinas = rutinas.filter(
            Q(nombre__icontains=consulta)
            | Q(descripcion__icontains=consulta)
            | Q(objetivo__icontains=consulta)
        )

    return render(
        request,
        "panel/rutinas_lista.html",
        {
            "panel_section": "rutinas",
            "rutinas": rutinas,
            "consulta": consulta,
        },
    )


@panel_access_required
def rutina_crear(request):
    if request.method == "POST":
        form = RutinaForm(request.POST)

        if form.is_valid():
            rutina = form.save()
            messages.success(
                request,
                f"La rutina «{rutina.nombre}» se creó correctamente.",
            )
            return redirect("panel:rutina_ejercicios", pk=rutina.pk)
    else:
        form = RutinaForm()

    return render(
        request,
        "panel/rutina_form.html",
        {
            "panel_section": "rutinas",
            "form": form,
            "titulo": "Nueva rutina",
            "descripcion": (
                "Crea una rutina y después añade sus ejercicios en orden."
            ),
            "url_cancelar": "panel:rutinas",
        },
    )


@panel_access_required
def rutina_editar(request, pk):
    rutina = get_object_or_404(Rutina, pk=pk)

    if request.method == "POST":
        form = RutinaForm(request.POST, instance=rutina)

        if form.is_valid():
            rutina = form.save()
            messages.success(
                request,
                f"La rutina «{rutina.nombre}» se actualizó correctamente.",
            )
            return redirect("panel:rutinas")
    else:
        form = RutinaForm(instance=rutina)

    return render(
        request,
        "panel/rutina_form.html",
        {
            "panel_section": "rutinas",
            "form": form,
            "rutina": rutina,
            "titulo": "Editar rutina",
            "descripcion": f"Actualiza los datos de «{rutina.nombre}».",
            "url_cancelar": "panel:rutinas",
        },
    )


@panel_access_required
def rutina_ejercicios(request, pk):
    rutina = get_object_or_404(Rutina, pk=pk)
    asociaciones = (
        rutina.rutina_ejercicios.select_related(
            "ejercicio__categoria"
        ).order_by("orden", "pk")
    )

    return render(
        request,
        "panel/rutina_ejercicios.html",
        {
            "panel_section": "rutinas",
            "rutina": rutina,
            "asociaciones": asociaciones,
        },
    )


@panel_access_required
def rutina_ejercicio_agregar(request, pk):
    rutina = get_object_or_404(Rutina, pk=pk)
    asociacion = RutinaEjercicio(rutina=rutina)

    if request.method == "POST":
        form = RutinaEjercicioForm(request.POST, instance=asociacion)

        if form.is_valid():
            asociacion = form.save()
            messages.success(
                request,
                f"«{asociacion.ejercicio.nombre}» se añadió a la rutina.",
            )
            return redirect("panel:rutina_ejercicios", pk=rutina.pk)
    else:
        form = RutinaEjercicioForm(instance=asociacion)

    return render(
        request,
        "panel/rutina_ejercicio_form.html",
        {
            "panel_section": "rutinas",
            "rutina": rutina,
            "form": form,
            "titulo": "Añadir ejercicio",
            "descripcion": f"Selecciona un ejercicio para «{rutina.nombre}».",
        },
    )


@panel_access_required
def rutina_ejercicio_editar(request, pk, asociacion_pk):
    rutina = get_object_or_404(Rutina, pk=pk)
    asociacion = get_object_or_404(
        RutinaEjercicio.objects.select_related("ejercicio"),
        pk=asociacion_pk,
        rutina=rutina,
    )

    if request.method == "POST":
        form = RutinaEjercicioForm(request.POST, instance=asociacion)

        if form.is_valid():
            asociacion = form.save()
            messages.success(
                request,
                f"La configuración de «{asociacion.ejercicio.nombre}» se actualizó.",
            )
            return redirect("panel:rutina_ejercicios", pk=rutina.pk)
    else:
        form = RutinaEjercicioForm(instance=asociacion)

    return render(
        request,
        "panel/rutina_ejercicio_form.html",
        {
            "panel_section": "rutinas",
            "rutina": rutina,
            "asociacion": asociacion,
            "form": form,
            "titulo": "Editar ejercicio de la rutina",
            "descripcion": (
                f"Ajusta el orden o las notas de "
                f"«{asociacion.ejercicio.nombre}»."
            ),
        },
    )


@panel_access_required
def rutina_ejercicio_eliminar(request, pk, asociacion_pk):
    rutina = get_object_or_404(Rutina, pk=pk)
    asociacion = get_object_or_404(
        RutinaEjercicio.objects.select_related("ejercicio"),
        pk=asociacion_pk,
        rutina=rutina,
    )

    if request.method == "POST":
        nombre = asociacion.ejercicio.nombre
        asociacion.delete()
        messages.success(
            request,
            f"«{nombre}» se quitó de la rutina.",
        )
        return redirect("panel:rutina_ejercicios", pk=rutina.pk)

    return render(
        request,
        "panel/confirmar_accion.html",
        {
            "panel_section": "rutinas",
            "titulo": "Quitar ejercicio de la rutina",
            "mensaje": (
                f"¿Deseas quitar «{asociacion.ejercicio.nombre}» de la rutina "
                f"«{rutina.nombre}»?"
            ),
            "objeto": asociacion,
            "dependencias": [],
            "puede_confirmar": True,
            "texto_confirmar": "Quitar de la rutina",
            "url_cancelar": "panel:rutina_ejercicios",
            "url_cancelar_kwargs": rutina.pk,
        },
    )


@panel_access_required
def usuarios_lista(request):
    usuarios = User.objects.annotate(
        total_rutinas_guardadas=Count("rutinas_guardadas")
    ).order_by("username")

    consulta = request.GET.get("q", "").strip()
    if consulta:
        usuarios = usuarios.filter(
            Q(username__icontains=consulta)
            | Q(email__icontains=consulta)
            | Q(first_name__icontains=consulta)
            | Q(last_name__icontains=consulta)
        )

    estado = request.GET.get("estado", "").strip()
    if estado == "activos":
        usuarios = usuarios.filter(is_active=True)
    elif estado == "inactivos":
        usuarios = usuarios.filter(is_active=False)
    elif estado == "staff":
        usuarios = usuarios.filter(is_staff=True)
    else:
        estado = ""

    return render(
        request,
        "panel/usuarios_lista.html",
        {
            "panel_section": "usuarios",
            "usuarios": usuarios,
            "consulta": consulta,
            "estado": estado,
        },
    )


@panel_access_required
@require_POST
def usuario_estado(request, pk):
    usuario = get_object_or_404(User, pk=pk)

    if usuario.pk == request.user.pk and usuario.is_active:
        messages.error(
            request,
            "No puedes desactivar tu propia cuenta desde el panel.",
        )
        return redirect("panel:usuarios")

    usuario.is_active = not usuario.is_active
    usuario.save(update_fields=["is_active"])

    if usuario.is_active:
        messages.success(
            request,
            f"La cuenta «{usuario.get_username()}» se activó correctamente.",
        )
    else:
        messages.success(
            request,
            f"La cuenta «{usuario.get_username()}» se desactivó correctamente.",
        )

    return redirect("panel:usuarios")
