from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class NavegacionHeaderTests(TestCase):
    def setUp(self):
        self.url = reverse("inicio")
        self.user = User.objects.create_user(
            username="laura",
            email="laura@example.com",
            password="ClaveSegura2026!",
        )

    def _header(self, response):
        return response.content.decode().split("</header>", 1)[0]

    def test_header_visitante_muestra_acceso_publico(self):
        response = self.client.get(self.url)
        header = self._header(response)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Iniciar sesión", header)
        self.assertIn("Registrarse", header)
        self.assertIn("Rutinas", header)
        self.assertIn(f'href="{reverse("rutinas:lista")}"', header)
        self.assertNotIn("Mi perfil", header)
        self.assertNotIn("Cerrar sesión", header)

    def test_header_autenticado_muestra_perfil_y_logout_post(self):
        self.client.force_login(self.user)

        response = self.client.get(self.url)
        header = self._header(response)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Mi perfil", header)
        self.assertIn("Rutinas", header)
        self.assertIn(f'href="{reverse("rutinas:lista")}"', header)
        self.assertIn('method="post"', header)
        self.assertIn(f'action="{reverse("usuarios:logout")}"', header)
        self.assertIn("csrfmiddlewaretoken", header)
        self.assertNotIn("Iniciar sesión", header)
        self.assertNotIn("Registrarse", header)

    def test_catalogo_muestra_enlace_rutinas_para_visitante(self):
        response = self.client.get(reverse("ejercicios:lista"))
        header = self._header(response)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Rutinas", header)
        self.assertIn(f'href="{reverse("rutinas:lista")}"', header)
