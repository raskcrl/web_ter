from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ejercicios.models import Categoria, Ejercicio
from rutinas.models import Rutina, RutinaEjercicio

User = get_user_model()


class AccesoPanelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.password = "ClaveSegura2026!"
        cls.usuario_normal = User.objects.create_user(
            username="usuario_normal",
            email="normal@example.com",
            password=cls.password,
        )
        cls.administrador = User.objects.create_user(
            username="administrador",
            email="admin@example.com",
            password=cls.password,
            is_staff=True,
        )
        cls.administrador_inactivo = User.objects.create_user(
            username="admin_inactivo",
            email="inactivo@example.com",
            password=cls.password,
            is_staff=True,
            is_active=False,
        )

    def setUp(self):
        self.url = reverse("panel:dashboard")

    def test_anonimo_redirige_al_login(self):
        response = self.client.get(self.url)

        self.assertRedirects(
            response,
            f"{reverse('usuarios:login')}?next={self.url}",
        )

    def test_usuario_normal_autenticado_recibe_403(self):
        self.client.force_login(self.usuario_normal)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 403)

    def test_staff_accede_al_dashboard(self):
        self.client.force_login(self.administrador)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "panel/base_panel.html")
        self.assertTemplateUsed(response, "panel/dashboard.html")
        self.assertContains(response, "Panel administrativo")
        self.assertContains(response, self.administrador.username)

    def test_staff_inactivo_no_accede(self):
        self.client.force_login(self.administrador_inactivo)

        response = self.client.get(self.url)

        self.assertRedirects(
            response,
            f"{reverse('usuarios:login')}?next={self.url}",
        )


class EnlacePanelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.password = "ClaveSegura2026!"
        cls.usuario_normal = User.objects.create_user(
            username="usuario_normal",
            email="normal@example.com",
            password=cls.password,
        )
        cls.administrador = User.objects.create_user(
            username="administrador",
            email="admin@example.com",
            password=cls.password,
            is_staff=True,
        )

    def _header(self, response):
        return response.content.decode().split("</header>", 1)[0]

    def _urls_con_header(self):
        return [
            ("inicio", reverse("inicio")),
            ("catalogo", reverse("ejercicios:lista")),
            ("rutinas", reverse("rutinas:lista")),
            ("cuenta", reverse("usuarios:password_change")),
        ]

    def test_administrador_ve_enlace_panel_en_los_cuatro_headers(self):
        self.client.force_login(self.administrador)

        for nombre, url in self._urls_con_header():
            with self.subTest(header=nombre):
                response = self.client.get(url)

                self.assertEqual(response.status_code, 200)
                header = self._header(response)
                self.assertIn(
                    f'href="{reverse("panel:dashboard")}"',
                    header,
                )
                self.assertIn("Panel", header)

    def test_usuario_normal_no_ve_enlace_panel(self):
        self.client.force_login(self.usuario_normal)

        for nombre, url in self._urls_con_header():
            with self.subTest(header=nombre):
                response = self.client.get(url)

                self.assertEqual(response.status_code, 200)
                header = self._header(response)
                self.assertNotIn(
                    f'href="{reverse("panel:dashboard")}"',
                    header,
                )
                self.assertNotIn(">Panel<", header)

    def test_visitante_no_ve_enlace_panel(self):
        urls = [
            ("inicio", reverse("inicio")),
            ("catalogo", reverse("ejercicios:lista")),
            ("rutinas", reverse("rutinas:lista")),
            ("cuenta", reverse("usuarios:login")),
        ]

        for nombre, url in urls:
            with self.subTest(header=nombre):
                response = self.client.get(url)

                self.assertEqual(response.status_code, 200)
                header = self._header(response)
                self.assertNotIn(
                    f'href="{reverse("panel:dashboard")}"',
                    header,
                )
                self.assertNotIn(">Panel<", header)


class LogoutDesdePanelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.administrador = User.objects.create_user(
            username="administrador",
            email="admin@example.com",
            password="ClaveSegura2026!",
            is_staff=True,
        )

    def test_logout_post_con_csrf_funciona(self):
        cliente = Client(enforce_csrf_checks=True)
        cliente.force_login(self.administrador)

        response = cliente.get(reverse("panel:dashboard"))
        self.assertEqual(response.status_code, 200)

        token = cliente.cookies["csrftoken"].value
        response = cliente.post(
            reverse("usuarios:logout"),
            {"csrfmiddlewaretoken": token},
        )

        self.assertRedirects(response, reverse("inicio"))
        self.assertNotIn("_auth_user_id", cliente.session)

    def test_logout_post_sin_csrf_es_rechazado(self):
        cliente = Client(enforce_csrf_checks=True)
        cliente.force_login(self.administrador)

        response = cliente.post(reverse("usuarios:logout"))

        self.assertEqual(response.status_code, 403)
        self.assertIn("_auth_user_id", cliente.session)


class AccesoSeccionesPanelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.password = "ClaveSegura2026!"
        cls.administrador = User.objects.create_user(
            username="admin_secciones",
            email="admin_secciones@example.com",
            password=cls.password,
            is_staff=True,
        )
        cls.usuario_normal = User.objects.create_user(
            username="normal_secciones",
            email="normal_secciones@example.com",
            password=cls.password,
        )
        cls.categoria = Categoria.objects.create(nombre="Acceso")
        cls.ejercicio = Ejercicio.objects.create(
            categoria=cls.categoria,
            nombre="Ejercicio de acceso",
            instrucciones="Instrucciones de prueba.",
        )
        cls.rutina = Rutina.objects.create(nombre="Rutina de acceso")
        cls.asociacion = RutinaEjercicio.objects.create(
            rutina=cls.rutina,
            ejercicio=cls.ejercicio,
            orden=1,
        )

    def _rutas(self):
        return [
            reverse("panel:dashboard"),
            reverse("panel:categorias"),
            reverse("panel:categoria_crear"),
            reverse("panel:categoria_editar", args=[self.categoria.pk]),
            reverse("panel:categoria_eliminar", args=[self.categoria.pk]),
            reverse("panel:ejercicios"),
            reverse("panel:ejercicio_crear"),
            reverse("panel:ejercicio_editar", args=[self.ejercicio.pk]),
            reverse("panel:ejercicio_eliminar", args=[self.ejercicio.pk]),
            reverse("panel:rutinas"),
            reverse("panel:rutina_crear"),
            reverse("panel:rutina_editar", args=[self.rutina.pk]),
            reverse("panel:rutina_ejercicios", args=[self.rutina.pk]),
            reverse(
                "panel:rutina_ejercicio_agregar",
                args=[self.rutina.pk],
            ),
            reverse(
                "panel:rutina_ejercicio_editar",
                args=[self.rutina.pk, self.asociacion.pk],
            ),
            reverse(
                "panel:rutina_ejercicio_eliminar",
                args=[self.rutina.pk, self.asociacion.pk],
            ),
            reverse("panel:usuarios"),
        ]

    def test_visitante_redirige_al_login_en_todas_las_secciones(self):
        for url in self._rutas():
            with self.subTest(url=url):
                response = self.client.get(url)

                self.assertRedirects(
                    response,
                    f"{reverse('usuarios:login')}?next={url}",
                )

    def test_usuario_normal_recibe_403_en_todas_las_secciones(self):
        self.client.force_login(self.usuario_normal)

        for url in self._rutas():
            with self.subTest(url=url):
                response = self.client.get(url)

                self.assertEqual(response.status_code, 403)

    def test_administrador_accede_a_todas_las_secciones(self):
        self.client.force_login(self.administrador)

        for url in self._rutas():
            with self.subTest(url=url):
                response = self.client.get(url)

                self.assertEqual(response.status_code, 200)


class DashboardPanelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.administrador = User.objects.create_user(
            username="admin_dashboard",
            email="admin_dashboard@example.com",
            password="ClaveSegura2026!",
            is_staff=True,
        )
        User.objects.create_user(
            username="usuario_dashboard",
            email="usuario_dashboard@example.com",
            password="ClaveSegura2026!",
        )
        cls.categoria = Categoria.objects.create(nombre="Dashboard")
        cls.ejercicio = Ejercicio.objects.create(
            categoria=cls.categoria,
            nombre="Ejercicio dashboard",
            instrucciones="Instrucciones.",
        )
        cls.rutina = Rutina.objects.create(nombre="Rutina dashboard")

    def test_dashboard_muestra_conteos_reales(self):
        self.client.force_login(self.administrador)

        response = self.client.get(reverse("panel:dashboard"))

        self.assertEqual(response.context["total_categorias"], 1)
        self.assertEqual(response.context["total_ejercicios"], 1)
        self.assertEqual(response.context["total_rutinas"], 1)
        self.assertEqual(response.context["total_usuarios"], 2)
        self.assertContains(response, self.ejercicio.nombre)
        self.assertContains(response, self.rutina.nombre)
        self.assertNotContains(response, "Próximamente")


class CategoriasPanelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.administrador = User.objects.create_user(
            username="admin_categorias",
            email="admin_categorias@example.com",
            password="ClaveSegura2026!",
            is_staff=True,
        )
        cls.categoria = Categoria.objects.create(
            nombre="Fuerza",
            descripcion="Ejercicios de fuerza",
            orden=1,
        )
        cls.otra_categoria = Categoria.objects.create(
            nombre="Cardio",
            descripcion="Trabajo cardiovascular",
            orden=2,
        )
        cls.categoria_con_ejercicio = Categoria.objects.create(
            nombre="Protegida",
            orden=3,
        )
        Ejercicio.objects.create(
            categoria=cls.categoria_con_ejercicio,
            nombre="Ejercicio protegido",
            instrucciones="No eliminar la categoría.",
        )

    def setUp(self):
        self.client.force_login(self.administrador)

    def test_lista_y_busqueda_de_categorias(self):
        response = self.client.get(reverse("panel:categorias"))

        self.assertContains(response, "Fuerza")
        self.assertContains(response, "Cardio")

        response = self.client.get(
            reverse("panel:categorias"),
            {"q": "cardio"},
        )

        self.assertContains(response, "Cardio")
        self.assertNotContains(response, "Fuerza")

    def test_crear_categoria(self):
        response = self.client.post(
            reverse("panel:categoria_crear"),
            {
                "nombre": "Movilidad",
                "descripcion": "Rutinas de movilidad",
                "activa": "on",
                "orden": "4",
            },
        )

        self.assertRedirects(response, reverse("panel:categorias"))
        categoria = Categoria.objects.get(nombre="Movilidad")
        self.assertEqual(categoria.slug, "movilidad")
        self.assertTrue(categoria.activa)

    def test_editar_categoria(self):
        response = self.client.post(
            reverse("panel:categoria_editar", args=[self.categoria.pk]),
            {
                "nombre": "Fuerza actualizada",
                "descripcion": "Nueva descripción",
                "orden": "5",
            },
        )

        self.assertRedirects(response, reverse("panel:categorias"))
        self.categoria.refresh_from_db()
        self.assertEqual(self.categoria.nombre, "Fuerza actualizada")
        self.assertFalse(self.categoria.activa)
        self.assertEqual(self.categoria.orden, 5)

    def test_no_elimina_categoria_con_ejercicios(self):
        url = reverse(
            "panel:categoria_eliminar",
            args=[self.categoria_con_ejercicio.pk],
        )
        response = self.client.get(url)

        self.assertFalse(response.context["puede_confirmar"])

        self.client.post(url)

        self.assertTrue(
            Categoria.objects.filter(pk=self.categoria_con_ejercicio.pk).exists()
        )

    def test_elimina_categoria_sin_dependencias(self):
        response = self.client.post(
            reverse("panel:categoria_eliminar", args=[self.otra_categoria.pk])
        )

        self.assertRedirects(response, reverse("panel:categorias"))
        self.assertFalse(
            Categoria.objects.filter(pk=self.otra_categoria.pk).exists()
        )


class EjerciciosPanelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.administrador = User.objects.create_user(
            username="admin_ejercicios",
            email="admin_ejercicios@example.com",
            password="ClaveSegura2026!",
            is_staff=True,
        )
        cls.categoria = Categoria.objects.create(nombre="Fuerza panel")
        cls.ejercicio = Ejercicio.objects.create(
            categoria=cls.categoria,
            nombre="Sentadilla",
            descripcion="Ejercicio de piernas",
            instrucciones="Baja con control.",
            dificultad=Ejercicio.Dificultad.PRINCIPIANTE,
            duracion_minutos=15,
        )
        cls.rutina = Rutina.objects.create(nombre="Rutina protegida")
        RutinaEjercicio.objects.create(
            rutina=cls.rutina,
            ejercicio=cls.ejercicio,
            orden=1,
        )

    def setUp(self):
        self.client.force_login(self.administrador)

    def test_lista_y_filtros_de_ejercicios(self):
        response = self.client.get(reverse("panel:ejercicios"))

        self.assertContains(response, "Sentadilla")
        self.assertContains(response, "Fuerza panel")

        response = self.client.get(
            reverse("panel:ejercicios"),
            {"q": "no existe"},
        )

        self.assertNotContains(response, "Sentadilla")

    def test_crear_ejercicio(self):
        response = self.client.post(
            reverse("panel:ejercicio_crear"),
            {
                "categoria": self.categoria.pk,
                "nombre": "Plancha",
                "descripcion": "Trabajo de core",
                "instrucciones": "Mantén el cuerpo alineado.",
                "dificultad": Ejercicio.Dificultad.INTERMEDIO,
                "duracion_minutos": "10",
                "video_url": "",
                "activo": "on",
            },
        )

        self.assertRedirects(response, reverse("panel:ejercicios"))
        ejercicio = Ejercicio.objects.get(nombre="Plancha")
        self.assertEqual(ejercicio.slug, "plancha")
        self.assertEqual(ejercicio.duracion_minutos, 10)
        self.assertTrue(ejercicio.activo)

    def test_editar_ejercicio(self):
        response = self.client.post(
            reverse("panel:ejercicio_editar", args=[self.ejercicio.pk]),
            {
                "categoria": self.categoria.pk,
                "nombre": "Sentadilla modificada",
                "descripcion": "Descripción nueva",
                "instrucciones": "Instrucciones nuevas.",
                "dificultad": Ejercicio.Dificultad.AVANZADO,
                "duracion_minutos": "20",
                "video_url": "https://example.com/video",
                "activo": "",
            },
        )

        self.assertRedirects(response, reverse("panel:ejercicios"))
        self.ejercicio.refresh_from_db()
        self.assertEqual(self.ejercicio.nombre, "Sentadilla modificada")
        self.assertEqual(
            self.ejercicio.dificultad,
            Ejercicio.Dificultad.AVANZADO,
        )
        self.assertFalse(self.ejercicio.activo)

    def test_no_elimina_ejercicio_usado_en_rutina(self):
        url = reverse("panel:ejercicio_eliminar", args=[self.ejercicio.pk])
        response = self.client.get(url)

        self.assertFalse(response.context["puede_confirmar"])
        self.assertContains(response, "Rutina protegida")

        self.client.post(url)

        self.assertTrue(Ejercicio.objects.filter(pk=self.ejercicio.pk).exists())

    def test_elimina_ejercicio_sin_dependencias(self):
        ejercicio = Ejercicio.objects.create(
            categoria=self.categoria,
            nombre="Ejercicio libre",
            instrucciones="Se puede eliminar.",
        )

        response = self.client.post(
            reverse("panel:ejercicio_eliminar", args=[ejercicio.pk])
        )

        self.assertRedirects(response, reverse("panel:ejercicios"))
        self.assertFalse(Ejercicio.objects.filter(pk=ejercicio.pk).exists())


class RutinasPanelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.administrador = User.objects.create_user(
            username="admin_rutinas",
            email="admin_rutinas@example.com",
            password="ClaveSegura2026!",
            is_staff=True,
        )
        cls.categoria = Categoria.objects.create(nombre="Fuerza rutinas")
        cls.ejercicio_1 = Ejercicio.objects.create(
            categoria=cls.categoria,
            nombre="Ejercicio uno",
            instrucciones="Instrucciones uno.",
        )
        cls.ejercicio_2 = Ejercicio.objects.create(
            categoria=cls.categoria,
            nombre="Ejercicio dos",
            instrucciones="Instrucciones dos.",
        )
        cls.rutina = Rutina.objects.create(nombre="Rutina base", orden=1)
        cls.asociacion = RutinaEjercicio.objects.create(
            rutina=cls.rutina,
            ejercicio=cls.ejercicio_1,
            orden=1,
        )

    def setUp(self):
        self.client.force_login(self.administrador)

    def test_lista_y_busqueda_de_rutinas(self):
        response = self.client.get(reverse("panel:rutinas"))

        self.assertContains(response, "Rutina base")

        response = self.client.get(
            reverse("panel:rutinas"),
            {"q": "no existe"},
        )

        self.assertNotContains(response, "Rutina base")

    def test_crear_rutina_redirige_a_sus_ejercicios(self):
        response = self.client.post(
            reverse("panel:rutina_crear"),
            {
                "nombre": "Rutina nueva",
                "descripcion": "Descripción",
                "objetivo": "Objetivo",
                "activa": "on",
                "orden": "2",
            },
        )

        rutina = Rutina.objects.get(nombre="Rutina nueva")
        self.assertRedirects(
            response,
            reverse("panel:rutina_ejercicios", args=[rutina.pk]),
        )

    def test_editar_rutina(self):
        response = self.client.post(
            reverse("panel:rutina_editar", args=[self.rutina.pk]),
            {
                "nombre": "Rutina actualizada",
                "descripcion": "Nueva descripción",
                "objetivo": "Nuevo objetivo",
                "orden": "3",
            },
        )

        self.assertRedirects(response, reverse("panel:rutinas"))
        self.rutina.refresh_from_db()
        self.assertEqual(self.rutina.nombre, "Rutina actualizada")
        self.assertFalse(self.rutina.activa)

    def test_agregar_ejercicio_a_rutina(self):
        response = self.client.post(
            reverse(
                "panel:rutina_ejercicio_agregar",
                args=[self.rutina.pk],
            ),
            {
                "ejercicio": self.ejercicio_2.pk,
                "orden": "2",
                "notas": "Mantener buen ritmo.",
            },
        )

        self.assertRedirects(
            response,
            reverse("panel:rutina_ejercicios", args=[self.rutina.pk]),
        )
        asociacion = RutinaEjercicio.objects.get(
            rutina=self.rutina,
            ejercicio=self.ejercicio_2,
        )
        self.assertEqual(asociacion.orden, 2)
        self.assertEqual(asociacion.notas, "Mantener buen ritmo.")

    def test_no_permite_duplicar_ejercicio_en_rutina(self):
        response = self.client.post(
            reverse(
                "panel:rutina_ejercicio_agregar",
                args=[self.rutina.pk],
            ),
            {
                "ejercicio": self.ejercicio_1.pk,
                "orden": "2",
                "notas": "",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "Este ejercicio ya forma parte de la rutina.",
        )
        self.assertEqual(
            RutinaEjercicio.objects.filter(
                rutina=self.rutina,
                ejercicio=self.ejercicio_1,
            ).count(),
            1,
        )

    def test_editar_asociacion_de_rutina(self):
        response = self.client.post(
            reverse(
                "panel:rutina_ejercicio_editar",
                args=[self.rutina.pk, self.asociacion.pk],
            ),
            {
                "ejercicio": self.ejercicio_2.pk,
                "orden": "7",
                "notas": "Notas actualizadas.",
            },
        )

        self.assertRedirects(
            response,
            reverse("panel:rutina_ejercicios", args=[self.rutina.pk]),
        )
        self.asociacion.refresh_from_db()
        self.assertEqual(self.asociacion.ejercicio, self.ejercicio_2)
        self.assertEqual(self.asociacion.orden, 7)
        self.assertEqual(self.asociacion.notas, "Notas actualizadas.")

    def test_quitar_ejercicio_pide_confirmacion_y_elimina(self):
        url = reverse(
            "panel:rutina_ejercicio_eliminar",
            args=[self.rutina.pk, self.asociacion.pk],
        )
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["puede_confirmar"])
        self.assertTrue(
            RutinaEjercicio.objects.filter(pk=self.asociacion.pk).exists()
        )

        response = self.client.post(url)

        self.assertRedirects(
            response,
            reverse("panel:rutina_ejercicios", args=[self.rutina.pk]),
        )
        self.assertFalse(
            RutinaEjercicio.objects.filter(pk=self.asociacion.pk).exists()
        )


class UsuariosPanelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.administrador = User.objects.create_user(
            username="admin_usuarios",
            email="admin_usuarios@example.com",
            password="ClaveSegura2026!",
            is_staff=True,
        )
        cls.usuario = User.objects.create_user(
            username="usuario_objetivo",
            email="objetivo@example.com",
            password="ClaveSegura2026!",
            first_name="Usuario",
            last_name="Objetivo",
        )
        cls.inactivo = User.objects.create_user(
            username="usuario_inactivo",
            email="inactivo@example.com",
            password="ClaveSegura2026!",
            is_active=False,
        )

    def setUp(self):
        self.client.force_login(self.administrador)

    def test_lista_y_busqueda_de_usuarios(self):
        response = self.client.get(
            reverse("panel:usuarios"),
            {"q": "objetivo"},
        )

        self.assertContains(response, "usuario_objetivo")
        self.assertNotContains(response, "usuario_inactivo")

    def test_filtro_por_estado(self):
        response = self.client.get(
            reverse("panel:usuarios"),
            {"estado": "inactivos"},
        )

        self.assertContains(response, "usuario_inactivo")
        self.assertNotContains(response, "usuario_objetivo")

    def test_desactivar_y_activar_usuario(self):
        url = reverse("panel:usuario_estado", args=[self.usuario.pk])

        response = self.client.post(url)

        self.assertRedirects(response, reverse("panel:usuarios"))
        self.usuario.refresh_from_db()
        self.assertFalse(self.usuario.is_active)

        self.client.post(url)

        self.usuario.refresh_from_db()
        self.assertTrue(self.usuario.is_active)

    def test_no_puede_desactivar_su_propia_cuenta(self):
        response = self.client.post(
            reverse("panel:usuario_estado", args=[self.administrador.pk])
        )

        self.assertRedirects(response, reverse("panel:usuarios"))
        self.administrador.refresh_from_db()
        self.assertTrue(self.administrador.is_active)

    def test_toggle_requiere_post(self):
        response = self.client.get(
            reverse("panel:usuario_estado", args=[self.usuario.pk])
        )

        self.assertEqual(response.status_code, 405)
        self.usuario.refresh_from_db()
        self.assertTrue(self.usuario.is_active)


class CsrfPanelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.administrador = User.objects.create_user(
            username="admin_csrf",
            email="admin_csrf@example.com",
            password="ClaveSegura2026!",
            is_staff=True,
        )

    def test_post_sin_csrf_es_rechazado(self):
        cliente = Client(enforce_csrf_checks=True)
        cliente.force_login(self.administrador)

        response = cliente.post(
            reverse("panel:categoria_crear"),
            {
                "nombre": "Sin CSRF",
                "descripcion": "",
                "activa": "on",
                "orden": "0",
            },
        )

        self.assertEqual(response.status_code, 403)
        self.assertFalse(Categoria.objects.filter(nombre="Sin CSRF").exists())

    def test_post_con_csrf_crea_categoria(self):
        cliente = Client(enforce_csrf_checks=True)
        cliente.force_login(self.administrador)

        response = cliente.get(reverse("panel:categoria_crear"))
        token = cliente.cookies["csrftoken"].value

        response = cliente.post(
            reverse("panel:categoria_crear"),
            {
                "csrfmiddlewaretoken": token,
                "nombre": "Con CSRF",
                "descripcion": "",
                "activa": "on",
                "orden": "0",
            },
        )

        self.assertRedirects(response, reverse("panel:categorias"))
        self.assertTrue(Categoria.objects.filter(nombre="Con CSRF").exists())
