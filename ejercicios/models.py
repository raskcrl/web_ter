from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils.text import slugify

TAMANO_MAXIMO_IMAGEN = 5 * 1024 * 1024


def validar_tamano_imagen(archivo):
    if archivo.size > TAMANO_MAXIMO_IMAGEN:
        raise ValidationError("La imagen no puede superar los 5 MB.")


def generar_slug(instancia, campo_nombre, campo_slug, longitud_maxima):
    base = slugify(getattr(instancia, campo_nombre))[:longitud_maxima] or "elemento"
    slug = base
    numero = 2

    while (
        instancia.__class__.objects.filter(**{campo_slug: slug})
        .exclude(pk=instancia.pk)
        .exists()
    ):
        sufijo = f"-{numero}"
        slug = f"{base[: longitud_maxima - len(sufijo)]}{sufijo}"
        numero += 1

    setattr(instancia, campo_slug, slug)


class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True, verbose_name="Nombre")
    slug = models.SlugField(max_length=120, unique=True, blank=True, verbose_name="Slug")
    descripcion = models.TextField(blank=True, verbose_name="Descripción")
    activa = models.BooleanField(default=True, verbose_name="Activa")
    orden = models.PositiveSmallIntegerField(default=0, verbose_name="Orden")
    creado = models.DateTimeField(auto_now_add=True, verbose_name="Creado")
    actualizado = models.DateTimeField(auto_now=True, verbose_name="Actualizado")

    class Meta:
        ordering = ("orden", "nombre")
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"

    def __str__(self):
        return self.nombre

    def save(self, *args, **kwargs):
        if not self.slug:
            generar_slug(self, "nombre", "slug", 120)
        super().save(*args, **kwargs)


class Ejercicio(models.Model):
    class Dificultad(models.TextChoices):
        PRINCIPIANTE = "principiante", "Principiante"
        INTERMEDIO = "intermedio", "Intermedio"
        AVANZADO = "avanzado", "Avanzado"

    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.PROTECT,
        related_name="ejercicios",
        verbose_name="Categoría",
    )
    nombre = models.CharField(max_length=150, verbose_name="Nombre")
    slug = models.SlugField(max_length=170, unique=True, blank=True, verbose_name="Slug")
    descripcion = models.TextField(blank=True, verbose_name="Descripción")
    instrucciones = models.TextField(verbose_name="Instrucciones")
    dificultad = models.CharField(
        max_length=20,
        choices=Dificultad.choices,
        default=Dificultad.PRINCIPIANTE,
        verbose_name="Dificultad",
    )
    duracion_minutos = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        verbose_name="Duración en minutos",
    )
    imagen = models.ImageField(
        upload_to="ejercicios/%Y/%m/",
        blank=True,
        null=True,
        verbose_name="Imagen",
        validators=[
            FileExtensionValidator(
                allowed_extensions=("jpg", "jpeg", "png", "webp"),
                message="Solo se permiten imágenes JPG, JPEG, PNG o WEBP.",
            ),
            validar_tamano_imagen,
        ],
    )
    video_url = models.URLField(blank=True, verbose_name="URL del video")
    activo = models.BooleanField(default=True, verbose_name="Activo")
    creado = models.DateTimeField(auto_now_add=True, verbose_name="Creado")
    actualizado = models.DateTimeField(auto_now=True, verbose_name="Actualizado")

    class Meta:
        ordering = ("categoria__orden", "nombre")
        verbose_name = "Ejercicio"
        verbose_name_plural = "Ejercicios"
        indexes = [
            models.Index(fields=["activo"]),
        ]

    def __str__(self):
        return f"{self.nombre} ({self.categoria.nombre})"

    def save(self, *args, **kwargs):
        if not self.slug:
            generar_slug(self, "nombre", "slug", 170)
        super().save(*args, **kwargs)
