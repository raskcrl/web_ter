from django.conf import settings
from django.db import models

from ejercicios.models import generar_slug


class Rutina(models.Model):
    nombre = models.CharField(max_length=150, verbose_name="Nombre")
    slug = models.SlugField(max_length=170, unique=True, blank=True, verbose_name="Slug")
    descripcion = models.TextField(blank=True, verbose_name="Descripción")
    objetivo = models.TextField(blank=True, verbose_name="Objetivo")
    activa = models.BooleanField(default=True, verbose_name="Activa")
    orden = models.PositiveSmallIntegerField(default=0, verbose_name="Orden")
    ejercicios = models.ManyToManyField(
        "ejercicios.Ejercicio",
        through="RutinaEjercicio",
        related_name="rutinas",
        blank=True,
        verbose_name="Ejercicios",
    )
    creado = models.DateTimeField(auto_now_add=True, verbose_name="Creado")
    actualizado = models.DateTimeField(auto_now=True, verbose_name="Actualizado")

    class Meta:
        ordering = ("orden", "nombre")
        verbose_name = "Rutina"
        verbose_name_plural = "Rutinas"
        indexes = [
            models.Index(fields=["activa"], name="rutina_activa_idx"),
        ]

    def __str__(self):
        return self.nombre

    def save(self, *args, **kwargs):
        if not self.slug:
            generar_slug(self, "nombre", "slug", 170)
        super().save(*args, **kwargs)


class RutinaEjercicio(models.Model):
    rutina = models.ForeignKey(
        Rutina,
        on_delete=models.CASCADE,
        related_name="rutina_ejercicios",
        verbose_name="Rutina",
    )
    ejercicio = models.ForeignKey(
        "ejercicios.Ejercicio",
        on_delete=models.PROTECT,
        related_name="asociaciones_rutina",
        verbose_name="Ejercicio",
    )
    orden = models.PositiveSmallIntegerField(default=0, verbose_name="Orden")
    notas = models.TextField(blank=True, verbose_name="Notas")

    class Meta:
        ordering = ("orden", "pk")
        verbose_name = "Ejercicio de rutina"
        verbose_name_plural = "Ejercicios de rutina"
        constraints = [
            models.UniqueConstraint(
                fields=["rutina", "ejercicio"],
                name="rutina_ejercicio_unico",
            ),
        ]

    def __str__(self):
        return f"{self.rutina.nombre}: {self.ejercicio.nombre}"


class UsuarioRutina(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="rutinas_guardadas",
        verbose_name="Usuario",
    )
    rutina = models.ForeignKey(
        Rutina,
        on_delete=models.CASCADE,
        related_name="guardadas_por",
        verbose_name="Rutina",
    )
    guardado_en = models.DateTimeField(auto_now_add=True, verbose_name="Guardada en")

    class Meta:
        ordering = ("-guardado_en",)
        verbose_name = "Rutina guardada"
        verbose_name_plural = "Rutinas guardadas"
        constraints = [
            models.UniqueConstraint(
                fields=["usuario", "rutina"],
                name="usuario_rutina_unico",
            ),
        ]

    def __str__(self):
        return f"{self.usuario} - {self.rutina.nombre}"
