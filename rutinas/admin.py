from django.contrib import admin

from .models import Rutina, RutinaEjercicio, UsuarioRutina


class RutinaEjercicioInline(admin.TabularInline):
    model = RutinaEjercicio
    extra = 1
    fields = ("ejercicio", "orden", "notas")
    autocomplete_fields = ("ejercicio",)
    ordering = ("orden",)


@admin.register(Rutina)
class RutinaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "activa", "orden", "total_ejercicios", "creado")
    list_filter = ("activa",)
    search_fields = ("nombre", "descripcion", "objetivo")
    prepopulated_fields = {"slug": ("nombre",)}
    readonly_fields = ("creado", "actualizado")
    inlines = (RutinaEjercicioInline,)
    ordering = ("orden", "nombre")

    @admin.display(description="Ejercicios")
    def total_ejercicios(self, obj):
        return obj.rutina_ejercicios.count()


@admin.register(UsuarioRutina)
class UsuarioRutinaAdmin(admin.ModelAdmin):
    list_display = ("usuario", "rutina", "guardado_en")
    list_filter = ("rutina__activa", "guardado_en")
    search_fields = ("usuario__username", "usuario__email", "rutina__nombre")
    autocomplete_fields = ("usuario", "rutina")
    readonly_fields = ("guardado_en",)
    list_select_related = ("usuario", "rutina")
    date_hierarchy = "guardado_en"
    ordering = ("-guardado_en",)
