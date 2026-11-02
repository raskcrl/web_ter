from django.urls import path

from . import views

app_name = "rutinas"

urlpatterns = [
    path("", views.RutinaListView.as_view(), name="lista"),
    path("guardadas/", views.RutinaGuardadasView.as_view(), name="guardadas"),
    path("<slug:slug>/guardar/", views.guardar_rutina, name="guardar"),
    path("<slug:slug>/", views.RutinaDetailView.as_view(), name="detalle"),
]
