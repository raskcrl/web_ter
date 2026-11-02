from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.db.models.deletion import ProtectedError
from django.test import Client, TestCase
from django.urls import reverse

from ejercicios.models import Categoria, Ejercicio
from rutinas.models import Rutina, RutinaEjercicio, UsuarioRutina

User = get_user_model()


class RutinaModelTests(TestCase):
    def setUp(self):
        self.categoria = Categoria.objects.create(nombre="Fuerza")
        self.ejercicio = Ejercicio.objects.create(
            categoria=self.categoria,
            nombre="Sentadilla",
            instrucciones="Realiza una sentadilla controlada.",
        )

    def test_genera_slug_y_slugs_unicos(self):
        primera = Rutina.objects.create(nombre="Rutina de fuerza")
        segunda = Rutina.objects.create(nombre="Rutina de fuerza!")

        self.assertEqual(primera.slug, "rutina-de-fuerza")
        self.assertEqual(segunda.slug, "rutina-de-fuerza-2")

    def test_no_permite_eliminar_ejercicio_usado_en_rutina(self):
        rutina = Rutina.objects.create(nombre="Rutina protegida")
        RutinaEjercicio.objects.create(rutina=rutina, ejercicio=self.ejercicio)

        with self.assertRaises(ProtectedError):
            with transaction.atomic():
                self.ejercicio.delete()

    def test_no_permite_guardar_la_misma_rutina_dos_veces(self):
        usuario = User.objects.create_user(
            username="duplicado",
            email="duplicado@example.com",
            password="ClaveSegura2026!",
        )
        rutina = Rutina.objects.create(nombre="Rutina única")
        UsuarioRutina.objects.create(usuario=usuario, rutina=rutina)

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                UsuarioRutina.objects.create(usuario=usuario, rutina=rutina)


class RutinasPublicasTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.categoria = Categoria.objects.create(nombre="Movilidad", orden=1)
        cls.categoria_inactiva = Categoria.objects.create(
            nombre="Oculta",
            activa=False,
        )

        cls.ejercicio_activo = Ejercicio.objects.create(
            categoria=cls.categoria,
            nombre="Respiración diafragmática",
            descripcion="Ejercicio de respiración.",
            instrucciones="Inspira y espira lentamente.",
        )
        cls.ejercicio_inactivo = Ejercicio.objects.create(
            categoria=cls.categoria,
            nombre="Ejercicio inactivo",
            instrucciones="No debe mostrarse.",
            activo=False,
        )
        cls.ejercicio_categoria_inactiva = Ejercicio.objects.create(
            categoria=cls.categoria_inactiva,
            nombre="Ejercicio de categoría inactiva",
            instrucciones="No debe mostrarse.",
        )

        cls.ejercicio_orden_uno = Ejercicio.objects.create(
            categoria=cls.categoria,
            nombre="Ejercicio orden uno",
            instrucciones="Tercero en la secuencia.",
        )
        cls.ejercicio_orden_dos = Ejercicio.objects.create(
            categoria=cls.categoria,
            nombre="Ejercicio orden dos",
            instrucciones="Primero en la secuencia.",
        )
        cls.ejercicio_orden_tres = Ejercicio.objects.create(
            categoria=cls.categoria,
            nombre="Ejercicio orden tres",
            instrucciones="Segundo en la secuencia.",
        )

        cls.rutina = Rutina.objects.create(
            nombre="Rutina de relajación",
            descripcion="Secuencia suave para respirar.",
            objetivo="Favorecer la calma",
            activa=True,
            orden=1,
        )
        cls.rutina_inactiva = Rutina.objects.create(
            nombre="Rutina oculta",
            activa=False,
            orden=2,
        )

        cls.re_rutina_ejercicio = RutinaEjercicio.objects.create(
            rutina=cls.rutina,
            ejercicio=cls.ejercicio_activo,
            orden=4,
            notas="Realizar con calma.",
        )
        RutinaEjercicio.objects.create(
            rutina=cls.rutina,
            ejercicio=cls.ejercicio_inactivo,
            orden=2,
        )
        RutinaEjercicio.objects.create(
            rutina=cls.rutina,
            ejercicio=cls.ejercicio_categoria_inactiva,
            orden=3,
        )
        RutinaEjercicio.objects.create(
            rutina=cls.rutina,
            ejercicio=cls.ejercicio_orden_uno,
            orden=2,
        )
        RutinaEjercicio.objects.create(
            rutina=cls.rutina,
            ejercicio=cls.ejercicio_orden_dos,
            orden=0,
        )
        RutinaEjercicio.objects.create(
            rutina=cls.rutina,
            ejercicio=cls.ejercicio_orden_tres,
            orden=1,
        )

    def test_listado_publico_funciona(self):
        self.client.logout()
        response = self.client.get(reverse("rutinas:lista"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.rutina.nombre)
        self.assertNotContains(response, self.rutina_inactiva.nombre)

    def test_detalle_publico_funciona(self):
        self.client.logout()
        response = self.client.get(reverse("rutinas:detalle", args=[self.rutina.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.rutina.nombre)
        self.assertContains(response, self.ejercicio_activo.nombre)

    def test_no_se_muestran_rutinas_inactivas(self):
        response = self.client.get(reverse("rutinas:detalle", args=[self.rutina_inactiva.slug]))
        self.assertEqual(response.status_code, 404)

    def test_no_se_muestran_ejercicios_inactivos_o_de_categoria_inactiva(self):
        response = self.client.get(reverse("rutinas:detalle", args=[self.rutina.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.ejercicio_activo.nombre)
        self.assertNotContains(response, self.ejercicio_inactivo.nombre)
        self.assertNotContains(response, self.ejercicio_categoria_inactiva.nombre)

    def test_anonimo_puede_consultar(self):
        self.client.logout()
        self.assertEqual(self.client.get(reverse("rutinas:lista")).status_code, 200)
        self.assertEqual(
            self.client.get(reverse("rutinas:detalle", args=[self.rutina.slug])).status_code,
            200,
        )

    def test_ejercicios_aparecen_en_orden(self):
        response = self.client.get(reverse("rutinas:detalle", args=[self.rutina.slug]))
        nombres = [
            item.ejercicio.nombre
            for item in response.context["ejercicios_rutina"]
        ]
        self.assertEqual(
            nombres,
            [
                self.ejercicio_orden_dos.nombre,
                self.ejercicio_orden_tres.nombre,
                self.ejercicio_orden_uno.nombre,
                self.ejercicio_activo.nombre,
            ],
        )


class RutinasGuardadoTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.categoria = Categoria.objects.create(nombre="Equilibrio")
        cls.ejercicio = Ejercicio.objects.create(
            categoria=cls.categoria,
            nombre="Apoyo unipodal",
            instrucciones="Mantén el equilibrio.",
        )
        cls.rutina = Rutina.objects.create(nombre="Rutina equilibrio", activa=True)
        RutinaEjercicio.objects.create(rutina=cls.rutina, ejercicio=cls.ejercicio, orden=1)
        cls.rutina_inactiva = Rutina.objects.create(
            nombre="Rutina inactiva",
            activa=False,
        )
        cls.usuario1 = User.objects.create_user(
            username="ana",
            email="ana@example.com",
            password="ClaveSegura2026!",
        )
        cls.usuario2 = User.objects.create_user(
            username="luis",
            email="luis@example.com",
            password="ClaveSegura2026!",
        )

    def test_anonimo_no_puede_guardar(self):
        self.client.logout()
        response = self.client.post(
            reverse("rutinas:guardar", args=[self.rutina.slug]),
            {"accion": "guardar"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("usuarios:login"), response.url)
        self.assertIn("next=", response.url)
        self.assertFalse(
            UsuarioRutina.objects.filter(rutina=self.rutina).exists()
        )

    def test_usuario_autenticado_puede_guardar(self):
        self.client.force_login(self.usuario1)
        response = self.client.post(
            reverse("rutinas:guardar", args=[self.rutina.slug]),
            {"accion": "guardar"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            UsuarioRutina.objects.filter(usuario=self.usuario1, rutina=self.rutina).exists()
        )

    def test_usuario_puede_quitar_rutina_guardada(self):
        self.client.force_login(self.usuario1)
        UsuarioRutina.objects.create(usuario=self.usuario1, rutina=self.rutina)
        response = self.client.post(
            reverse("rutinas:guardar", args=[self.rutina.slug]),
            {"accion": "quitar"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(
            UsuarioRutina.objects.filter(usuario=self.usuario1, rutina=self.rutina).exists()
        )

    def test_no_se_pueden_guardar_duplicados(self):
        self.client.force_login(self.usuario1)
        self.client.post(reverse("rutinas:guardar", args=[self.rutina.slug]), {"accion": "guardar"})
        self.client.post(reverse("rutinas:guardar", args=[self.rutina.slug]), {"accion": "guardar"})
        self.assertEqual(
            UsuarioRutina.objects.filter(usuario=self.usuario1, rutina=self.rutina).count(),
            1,
        )

    def test_cada_usuario_ve_solo_sus_rutinas_guardadas(self):
        UsuarioRutina.objects.create(usuario=self.usuario1, rutina=self.rutina)
        UsuarioRutina.objects.create(usuario=self.usuario1, rutina=self.rutina_inactiva)
        self.client.force_login(self.usuario2)
        response = self.client.get(reverse("rutinas:guardadas"))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, self.rutina.nombre)
        self.client.force_login(self.usuario1)
        response = self.client.get(reverse("rutinas:guardadas"))
        self.assertContains(response, self.rutina.nombre)
        self.assertNotContains(response, self.rutina_inactiva.nombre)

    def test_guardadas_requiere_login(self):
        self.client.logout()
        response = self.client.get(reverse("rutinas:guardadas"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("usuarios:login"), response.url)

    def test_no_se_puede_guardar_una_rutina_inactiva(self):
        self.client.force_login(self.usuario1)
        response = self.client.post(
            reverse("rutinas:guardar", args=[self.rutina_inactiva.slug]),
            {"accion": "guardar"},
        )
        self.assertEqual(response.status_code, 404)
        self.assertFalse(
            UsuarioRutina.objects.filter(
                usuario=self.usuario1,
                rutina=self.rutina_inactiva,
            ).exists()
        )

    def test_get_no_modifica_rutinas_guardadas(self):
        self.client.force_login(self.usuario1)
        response = self.client.get(
            reverse("rutinas:guardar", args=[self.rutina.slug])
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(
            UsuarioRutina.objects.filter(
                usuario=self.usuario1,
                rutina=self.rutina,
            ).exists()
        )

    def test_post_sin_csrf_es_rechazado(self):
        cliente = Client(enforce_csrf_checks=True)
        cliente.force_login(self.usuario1)
        response = cliente.post(
            reverse("rutinas:guardar", args=[self.rutina.slug]),
            {"accion": "guardar"},
        )
        self.assertEqual(response.status_code, 403)
        self.assertFalse(
            UsuarioRutina.objects.filter(
                usuario=self.usuario1,
                rutina=self.rutina,
            ).exists()
        )
