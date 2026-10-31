from django.contrib import admin

from .models import PerfilUsuario


@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ("usuario", "foto", "actualizado")
    search_fields = ("usuario__username", "usuario__email")
    readonly_fields = ("actualizado",)
