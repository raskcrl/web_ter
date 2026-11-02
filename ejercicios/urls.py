from django.urls import path

from . import views

app_name = "ejercicios"

urlpatterns = [
    path("", views.EjercicioListView.as_view(), name="lista"),
    path(
        "categoria/<slug:slug>/",
        views.EjercicioListView.as_view(),
        name="por_categoria",
    ),
    path("<slug:slug>/", views.EjercicioDetailView.as_view(), name="detalle"),
]
