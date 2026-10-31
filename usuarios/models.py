from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models

TAMANO_MAXIMO_FOTO = 5 * 1024 * 1024


def validar_tamano_foto(archivo):
    if archivo.size > TAMANO_MAXIMO_FOTO:
        raise ValidationError("La foto no puede superar los 5 MB.")


class PerfilUsuario(models.Model):
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="perfil",
        verbose_name="Usuario",
    )
    foto = models.ImageField(
        upload_to="perfiles/%Y/%m/",
        blank=True,
        null=True,
        verbose_name="Foto de perfil",
        validators=[
            FileExtensionValidator(
                allowed_extensions=("jpg", "jpeg", "png", "webp"),
                message="Solo se permiten imágenes JPG, JPEG, PNG o WEBP.",
            ),
            validar_tamano_foto,
        ],
    )
    actualizado = models.DateTimeField(auto_now=True, verbose_name="Actualizado")

    class Meta:
        verbose_name = "Perfil de usuario"
        verbose_name_plural = "Perfiles de usuario"

    def __str__(self):
        return f"Perfil de {self.usuario.get_username()}"
