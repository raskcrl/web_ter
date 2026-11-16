from django.urls import path

from . import views

app_name = "panel"

urlpatterns = [
    path("", views.DashboardView.as_view(), name="dashboard"),
    path("categorias/", views.categorias_lista, name="categorias"),
    path(
        "categorias/nueva/",
        views.categoria_crear,
        name="categoria_crear",
    ),
    path(
        "categorias/<int:pk>/editar/",
        views.categoria_editar,
        name="categoria_editar",
    ),
    path(
        "categorias/<int:pk>/eliminar/",
        views.categoria_eliminar,
        name="categoria_eliminar",
    ),
    path("ejercicios/", views.ejercicios_lista, name="ejercicios"),
    path(
        "ejercicios/nuevo/",
        views.ejercicio_crear,
        name="ejercicio_crear",
    ),
    path(
        "ejercicios/<int:pk>/editar/",
        views.ejercicio_editar,
        name="ejercicio_editar",
    ),
    path(
        "ejercicios/<int:pk>/eliminar/",
        views.ejercicio_eliminar,
        name="ejercicio_eliminar",
    ),
    path("rutinas/", views.rutinas_lista, name="rutinas"),
    path("rutinas/nueva/", views.rutina_crear, name="rutina_crear"),
    path(
        "rutinas/<int:pk>/editar/",
        views.rutina_editar,
        name="rutina_editar",
    ),
    path(
        "rutinas/<int:pk>/ejercicios/",
        views.rutina_ejercicios,
        name="rutina_ejercicios",
    ),
    path(
        "rutinas/<int:pk>/ejercicios/agregar/",
        views.rutina_ejercicio_agregar,
        name="rutina_ejercicio_agregar",
    ),
    path(
        "rutinas/<int:pk>/ejercicios/<int:asociacion_pk>/editar/",
        views.rutina_ejercicio_editar,
        name="rutina_ejercicio_editar",
    ),
    path(
        "rutinas/<int:pk>/ejercicios/<int:asociacion_pk>/quitar/",
        views.rutina_ejercicio_eliminar,
        name="rutina_ejercicio_eliminar",
    ),
    path("usuarios/", views.usuarios_lista, name="usuarios"),
    path(
        "usuarios/<int:pk>/estado/",
        views.usuario_estado,
        name="usuario_estado",
    ),
]
