from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class RegistroTests(TestCase):
    def setUp(self):
        self.url = reverse("usuarios:registro")
        self.datos_validos = {
            "username": "nuevo_usuario",
            "email": "Nuevo@Example.com",
            "password1": "ClaveSegura2026!",
            "password2": "ClaveSegura2026!",
        }

    def test_muestra_formulario_de_registro(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "usuarios/registro.html")

    def test_registro_valido_crea_usuario_e_inicia_sesion(self):
        response = self.client.post(self.url, self.datos_validos)

        self.assertRedirects(response, reverse("usuarios:perfil"))
        user = User.objects.get(username="nuevo_usuario")
        self.assertEqual(user.email, "nuevo@example.com")
        self.assertEqual(int(self.client.session["_auth_user_id"]), user.pk)

    def test_rechaza_nombre_de_usuario_duplicado(self):
        User.objects.create_user(
            username="Nuevo_Usuario",
            email="existente@example.com",
            password="ClaveSegura2026!",
        )

        response = self.client.post(self.url, self.datos_validos)

        self.assertEqual(response.status_code, 200)
        self.assertIn("username", response.context["form"].errors)
        self.assertEqual(User.objects.count(), 1)

    def test_rechaza_correo_duplicado_sin_distinguir_mayusculas(self):
        User.objects.create_user(
            username="otro_usuario",
            email="nuevo@example.com",
            password="ClaveSegura2026!",
        )

        response = self.client.post(self.url, self.datos_validos)

        self.assertEqual(response.status_code, 200)
        self.assertIn("email", response.context["form"].errors)
        self.assertEqual(User.objects.count(), 1)

    def test_rechaza_confirmacion_de_contrasena_distinta(self):
        datos = {
            **self.datos_validos,
            "password2": "OtraClave2026!",
        }

        response = self.client.post(self.url, datos)

        self.assertEqual(response.status_code, 200)
        self.assertIn("password2", response.context["form"].errors)
        self.assertEqual(User.objects.count(), 0)

    def test_rechaza_contrasena_debil(self):
        datos = {
            **self.datos_validos,
            "password1": "12345678",
            "password2": "12345678",
        }

        response = self.client.post(self.url, datos)

        self.assertEqual(response.status_code, 200)
        self.assertIn("password2", response.context["form"].errors)
        self.assertEqual(User.objects.count(), 0)

    def test_correo_es_obligatorio(self):
        datos = {
            **self.datos_validos,
            "email": "",
        }

        response = self.client.post(self.url, datos)

        self.assertEqual(response.status_code, 200)
        self.assertIn("email", response.context["form"].errors)
        self.assertEqual(User.objects.count(), 0)

    def test_usuario_autenticado_es_redirigido_al_perfil(self):
        user = User.objects.create_user(
            username="autenticado",
            email="autenticado@example.com",
            password="ClaveSegura2026!",
        )
        self.client.force_login(user)

        response = self.client.get(self.url)

        self.assertRedirects(response, reverse("usuarios:perfil"))


class InicioSesionTests(TestCase):
    def setUp(self):
        self.url = reverse("usuarios:login")
        self.password = "ClaveSegura2026!"
        self.user = User.objects.create_user(
            username="laura",
            email="laura@example.com",
            password=self.password,
        )

    def test_muestra_formulario_de_inicio_de_sesion(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "usuarios/login.html")

    def test_inicio_de_sesion_valido_redirige_al_perfil(self):
        response = self.client.post(
            self.url,
            {"username": "laura", "password": self.password},
        )

        self.assertRedirects(response, reverse("usuarios:perfil"))
        self.assertEqual(int(self.client.session["_auth_user_id"]), self.user.pk)

    def test_inicio_de_sesion_invalido_muestra_error(self):
        response = self.client.post(
            self.url,
            {"username": "laura", "password": "incorrecta"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("_auth_user_id", self.client.session)
        errores = response.context["form"].non_field_errors()
        self.assertIn(
            "Usuario o contraseña incorrectos",
            " ".join(errores),
        )

    def test_usuario_autenticado_es_redirigido_al_perfil(self):
        self.client.force_login(self.user)

        response = self.client.get(self.url)

        self.assertRedirects(response, reverse("usuarios:perfil"))


class CierreSesionTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="laura",
            email="laura@example.com",
            password="ClaveSegura2026!",
        )
        self.url = reverse("usuarios:logout")

    def test_cierre_de_sesion_elimina_la_sesion(self):
        self.client.force_login(self.user)

        response = self.client.post(self.url)

        self.assertRedirects(response, reverse("inicio"))
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_cierre_de_sesion_no_permite_get(self):
        self.client.force_login(self.user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 405)


class PerfilTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="laura",
            email="laura@example.com",
            password="ClaveSegura2026!",
            first_name="Laura",
            last_name="Gómez",
        )
        self.url = reverse("usuarios:perfil")

    def test_acceso_anonimo_redirige_al_inicio_de_sesion(self):
        response = self.client.get(self.url)

        self.assertRedirects(
            response,
            f"{reverse('usuarios:login')}?next={self.url}",
        )

    def test_muestra_informacion_basica_del_usuario(self):
        self.client.force_login(self.user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "usuarios/perfil.html")
        self.assertContains(response, "laura")
        self.assertContains(response, "laura@example.com")

    def test_permite_editar_nombre_apellido_y_correo(self):
        self.client.force_login(self.user)

        response = self.client.post(
            self.url,
            {
                "first_name": "Laura Elena",
                "last_name": "Gómez Ruiz",
                "email": "LAURA.NUEVA@EXAMPLE.COM",
            },
        )

        self.assertRedirects(response, self.url)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "Laura Elena")
        self.assertEqual(self.user.last_name, "Gómez Ruiz")
        self.assertEqual(self.user.email, "laura.nueva@example.com")

    def test_rechaza_correo_de_otro_usuario(self):
        User.objects.create_user(
            username="otro",
            email="ocupado@example.com",
            password="ClaveSegura2026!",
        )
        self.client.force_login(self.user)

        response = self.client.post(
            self.url,
            {
                "first_name": "Laura",
                "last_name": "Gómez",
                "email": "ocupado@example.com",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("email", response.context["form"].errors)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, "laura@example.com")

    def test_permite_conservar_el_mismo_correo(self):
        self.client.force_login(self.user)

        response = self.client.post(
            self.url,
            {
                "first_name": "Laura",
                "last_name": "Gómez",
                "email": "laura@example.com",
            },
        )

        self.assertRedirects(response, self.url)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, "laura@example.com")
