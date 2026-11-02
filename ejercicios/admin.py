from django.contrib import admin

from .models import Categoria, Ejercicio


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "slug", "activa", "orden", "total_ejercicios")
    list_filter = ("activa",)
    search_fields = ("nombre", "descripcion")
    prepopulated_fields = {"slug": ("nombre",)}
    ordering = ("orden", "nombre")

    @admin.display(description="Ejercicios")
    def total_ejercicios(self, obj):
        return obj.ejercicios.count()


@admin.register(Ejercicio)
class EjercicioAdmin(admin.ModelAdmin):
    list_display = (
        "nombre",
        "categoria",
        "dificultad",
        "duracion_minutos",
        "activo",
    )
    list_filter = ("activo", "dificultad", "categoria")
    search_fields = ("nombre", "descripcion", "instrucciones", "categoria__nombre")
    prepopulated_fields = {"slug": ("nombre",)}
    autocomplete_fields = ("categoria",)
    readonly_fields = ("creado", "actualizado")
    list_select_related = ("categoria",)
    ordering = ("categoria__orden", "nombre")
