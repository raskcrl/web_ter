from django.test import TestCase
from django.urls import reverse

from .models import Categoria, Ejercicio


class CategoriaModelTests(TestCase):
    def test_genera_slug_desde_el_nombre(self):
        categoria = Categoria.objects.create(nombre="Fuerza y equilibrio")

        self.assertEqual(categoria.slug, "fuerza-y-equilibrio")

    def test_genera_slugs_unicos(self):
        primera = Categoria.objects.create(nombre="Fuerza")
        segunda = Categoria.objects.create(nombre="Fuerza!")

        self.assertEqual(primera.slug, "fuerza")
        self.assertEqual(segunda.slug, "fuerza-2")


class EjercicioModelTests(TestCase):
    def setUp(self):
        self.categoria = Categoria.objects.create(nombre="Movilidad")

    def test_genera_slug_y_relacion_con_categoria(self):
        ejercicio = Ejercicio.objects.create(
            categoria=self.categoria,
            nombre="Movilidad de hombros",
            instrucciones="Realiza movimientos circulares suaves.",
        )

        self.assertEqual(ejercicio.slug, "movilidad-de-hombros")
        self.assertEqual(ejercicio.categoria, self.categoria)
        self.assertIn(ejercicio, self.categoria.ejercicios.all())


class CatalogoViewsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.categoria = Categoria.objects.create(nombre="Equilibrio", orden=1)
        cls.categoria_inactiva = Categoria.objects.create(
            nombre="Categoría oculta",
            activa=False,
        )
        cls.ejercicio = Ejercicio.objects.create(
            categoria=cls.categoria,
            nombre="Apoyo unipodal",
            descripcion="Ejercicio de equilibrio básico.",
            instrucciones="Apoya una pierna y mantén la posición.",
            dificultad=Ejercicio.Dificultad.PRINCIPIANTE,
        )
        cls.ejercicio_inactivo = Ejercicio.objects.create(
            categoria=cls.categoria,
            nombre="Ejercicio oculto",
            instrucciones="No debe aparecer en el catálogo.",
            activo=False,
        )
        cls.ejercicio_categoria_inactiva = Ejercicio.objects.create(
            categoria=cls.categoria_inactiva,
            nombre="Ejercicio de categoría oculta",
            instrucciones="No debe aparecer en el catálogo.",
        )

    def test_listado_muestra_solo_ejercicios_activos(self):
        respuesta = self.client.get(reverse("ejercicios:lista"))

        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, self.ejercicio.nombre)
        self.assertNotContains(respuesta, self.ejercicio_inactivo.nombre)
        self.assertNotContains(respuesta, self.ejercicio_categoria_inactiva.nombre)

    def test_filtro_por_categoria(self):
        respuesta = self.client.get(
            reverse("ejercicios:por_categoria", args=[self.categoria.slug])
        )

        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, self.ejercicio.nombre)
        self.assertNotContains(respuesta, self.ejercicio_categoria_inactiva.nombre)

    def test_detalle_de_ejercicio(self):
        respuesta = self.client.get(
            reverse("ejercicios:detalle", args=[self.ejercicio.slug])
        )

        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, self.ejercicio.nombre)
        self.assertContains(respuesta, self.categoria.nombre)

    def test_detalle_de_ejercicio_inactivo_devuelve_404(self):
        respuesta = self.client.get(
            reverse("ejercicios:detalle", args=[self.ejercicio_inactivo.slug])
        )

        self.assertEqual(respuesta.status_code, 404)

    def test_categoria_inactiva_devuelve_404(self):
        respuesta = self.client.get(
            reverse("ejercicios:por_categoria", args=[self.categoria_inactiva.slug])
        )

        self.assertEqual(respuesta.status_code, 404)
