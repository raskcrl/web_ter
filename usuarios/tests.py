import os
import shutil
import tempfile
from io import BytesIO

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from PIL import Image

from .models import PerfilUsuario, TAMANO_MAXIMO_FOTO

User = get_user_model()


def crear_imagen(nombre="foto.png", color="green"):
    buffer = BytesIO()
    Image.new("RGB", (10, 10), color).save(buffer, format="PNG")
    return SimpleUploadedFile(
        nombre,
        buffer.getvalue(),
        content_type="image/png",
    )


def crear_imagen_grande():
    ancho = alto = 1600
    buffer = BytesIO()
    Image.frombytes(
        "RGB",
        (ancho, alto),
        os.urandom(ancho * alto * 3),
    ).save(buffer, format="PNG")
    return SimpleUploadedFile(
        "grande.png",
        buffer.getvalue(),
        content_type="image/png",
    )


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

    def test_inicio_de_sesion_respeta_la_url_solicitada(self):
        perfil_url = reverse("usuarios:perfil")

        response = self.client.post(
            f"{self.url}?next={perfil_url}",
            {"username": "laura", "password": self.password},
        )

        self.assertRedirects(response, perfil_url)


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

    def test_tras_cerrar_sesion_no_se_puede_acceder_al_perfil(self):
        self.client.force_login(self.user)

        self.client.post(self.url)

        perfil_url = reverse("usuarios:perfil")
        response = self.client.get(perfil_url)

        self.assertRedirects(
            response,
            f"{reverse('usuarios:login')}?next={perfil_url}",
        )
        self.assertNotIn("_auth_user_id", self.client.session)


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

    def test_muestra_mi_actividad_y_enlace_a_rutinas_guardadas(self):
        self.client.force_login(self.user)

        response = self.client.get(self.url)

        self.assertContains(response, "Mi actividad")
        self.assertContains(response, "Mis rutinas")
        self.assertContains(
            response,
            "Consulta las rutinas que has guardado en tu cuenta.",
        )
        self.assertContains(
            response,
            f'href="{reverse("rutinas:guardadas")}"',
        )

    def test_perfil_no_se_almacena_en_cache(self):
        self.client.force_login(self.user)

        response = self.client.get(self.url)

        self.assertIn("no-store", response["Cache-Control"])

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

    def test_edicion_solo_afecta_al_usuario_autenticado(self):
        otro = User.objects.create_user(
            username="otro",
            email="otro@example.com",
            password="ClaveSegura2026!",
            first_name="Otro",
            last_name="Usuario",
        )
        self.client.force_login(self.user)

        response = self.client.post(
            self.url,
            {
                "first_name": "Laura Elena",
                "last_name": "Gómez Ruiz",
                "email": "laura.nueva@example.com",
            },
        )

        self.assertRedirects(response, self.url)
        self.user.refresh_from_db()
        otro.refresh_from_db()
        self.assertEqual(self.user.first_name, "Laura Elena")
        self.assertEqual(self.user.email, "laura.nueva@example.com")
        self.assertEqual(otro.first_name, "Otro")
        self.assertEqual(otro.email, "otro@example.com")

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


class PerfilFotoTests(TestCase):
    def setUp(self):
        self.media_root = tempfile.mkdtemp()
        self.override_media = override_settings(MEDIA_ROOT=self.media_root)
        self.override_media.enable()
        self.addCleanup(self.override_media.disable)
        self.addCleanup(shutil.rmtree, self.media_root, ignore_errors=True)

        self.user = User.objects.create_user(
            username="laura",
            email="laura@example.com",
            password="ClaveSegura2026!",
        )
        self.client.force_login(self.user)
        self.url = reverse("usuarios:perfil_foto")
        self.perfil_url = reverse("usuarios:perfil")

    def test_muestra_avatar_predeterminado_sin_foto(self):
        response = self.client.get(self.perfil_url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "avatar-default.svg")

    def test_sube_foto_valida(self):
        response = self.client.post(self.url, {"foto": crear_imagen()})

        self.assertRedirects(response, self.perfil_url)
        perfil = PerfilUsuario.objects.get(usuario=self.user)
        self.assertTrue(perfil.foto)
        self.assertTrue(os.path.exists(perfil.foto.path))

        response = self.client.get(self.perfil_url)
        self.assertContains(response, perfil.foto.url)
        self.assertNotContains(response, "avatar-default.svg")

    def test_rechaza_extension_no_permitida(self):
        response = self.client.post(
            self.url,
            {"foto": crear_imagen("foto.txt")},
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("foto", response.context["foto_form"].errors)
        self.assertFalse(
            PerfilUsuario.objects.filter(usuario=self.user).exists()
        )

    def test_rechaza_contenido_que_no_es_imagen(self):
        archivo = SimpleUploadedFile(
            "foto.png",
            b"esto no es una imagen",
            content_type="image/png",
        )

        response = self.client.post(self.url, {"foto": archivo})

        self.assertEqual(response.status_code, 200)
        self.assertIn("foto", response.context["foto_form"].errors)
        self.assertFalse(
            PerfilUsuario.objects.filter(usuario=self.user).exists()
        )

    def test_rechaza_archivo_demasiado_grande(self):
        archivo = crear_imagen_grande()
        self.assertGreater(archivo.size, TAMANO_MAXIMO_FOTO)

        response = self.client.post(self.url, {"foto": archivo})

        self.assertEqual(response.status_code, 200)
        self.assertIn("foto", response.context["foto_form"].errors)
        self.assertFalse(
            PerfilUsuario.objects.filter(usuario=self.user).exists()
        )

    def test_cambia_foto_y_elimina_archivo_anterior(self):
        self.client.post(self.url, {"foto": crear_imagen(color="red")})
        perfil = PerfilUsuario.objects.get(usuario=self.user)
        nombre_anterior = perfil.foto.name
        ruta_anterior = perfil.foto.path

        response = self.client.post(
            self.url,
            {"foto": crear_imagen("nueva.png", color="blue")},
        )

        self.assertRedirects(response, self.perfil_url)
        perfil.refresh_from_db()
        self.assertNotEqual(perfil.foto.name, nombre_anterior)
        self.assertFalse(os.path.exists(ruta_anterior))
        self.assertTrue(os.path.exists(perfil.foto.path))

    def test_quita_foto_y_muestra_avatar_predeterminado(self):
        self.client.post(self.url, {"foto": crear_imagen()})
        perfil = PerfilUsuario.objects.get(usuario=self.user)
        ruta_anterior = perfil.foto.path

        response = self.client.post(self.url, {"eliminar_foto": "on"})

        self.assertRedirects(response, self.perfil_url)
        perfil.refresh_from_db()
        self.assertFalse(perfil.foto)
        self.assertFalse(os.path.exists(ruta_anterior))

        response = self.client.get(self.perfil_url)
        self.assertContains(response, "avatar-default.svg")

    def test_usuario_anonimo_no_puede_subir_foto(self):
        self.client.logout()

        response = self.client.post(self.url, {"foto": crear_imagen()})

        self.assertRedirects(
            response,
            f"{reverse('usuarios:login')}?next={self.url}",
        )
        self.assertFalse(
            PerfilUsuario.objects.filter(usuario=self.user).exists()
        )

    def test_get_redirige_al_perfil(self):
        response = self.client.get(self.url)

        self.assertRedirects(response, self.perfil_url)


class CambioPasswordTests(TestCase):
    def setUp(self):
        self.password = "ClaveSegura2026!"
        self.user = User.objects.create_user(
            username="laura",
            email="laura@example.com",
            password=self.password,
        )
        self.client.force_login(self.user)
        self.url = reverse("usuarios:password_change")
        self.perfil_url = reverse("usuarios:perfil")

    def test_muestra_formulario(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "usuarios/password_change.html")
        self.assertContains(response, "Contraseña actual")

    def test_cambio_exitoso_mantiene_sesion(self):
        response = self.client.post(
            self.url,
            {
                "old_password": self.password,
                "new_password1": "NuevaClave2026!",
                "new_password2": "NuevaClave2026!",
            },
            follow=True,
        )

        self.assertRedirects(response, self.perfil_url)
        self.assertContains(
            response,
            "Tu contraseña se actualizó correctamente.",
        )
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("NuevaClave2026!"))
        self.assertEqual(
            int(self.client.session["_auth_user_id"]),
            self.user.pk,
        )
        self.assertEqual(self.client.get(self.perfil_url).status_code, 200)

    def test_rechaza_contrasena_actual_incorrecta(self):
        response = self.client.post(
            self.url,
            {
                "old_password": "incorrecta",
                "new_password1": "NuevaClave2026!",
                "new_password2": "NuevaClave2026!",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("old_password", response.context["form"].errors)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(self.password))

    def test_rechaza_confirmacion_distinta(self):
        response = self.client.post(
            self.url,
            {
                "old_password": self.password,
                "new_password1": "NuevaClave2026!",
                "new_password2": "OtraClave2026!",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("new_password2", response.context["form"].errors)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(self.password))

    def test_rechaza_contrasena_debil(self):
        response = self.client.post(
            self.url,
            {
                "old_password": self.password,
                "new_password1": "12345678",
                "new_password2": "12345678",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("new_password2", response.context["form"].errors)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(self.password))

    def test_rechaza_contrasena_similar_al_usuario(self):
        response = self.client.post(
            self.url,
            {
                "old_password": self.password,
                "new_password1": "laura2026",
                "new_password2": "laura2026",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("new_password2", response.context["form"].errors)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(self.password))

    def test_usuario_anonimo_no_puede_cambiar_contrasena(self):
        self.client.logout()

        response = self.client.post(
            self.url,
            {
                "old_password": self.password,
                "new_password1": "NuevaClave2026!",
                "new_password2": "NuevaClave2026!",
            },
        )

        self.assertRedirects(
            response,
            f"{reverse('usuarios:login')}?next={self.url}",
        )
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(self.password))


class PerfilAnonimoTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="laura",
            email="laura@example.com",
            password="ClaveSegura2026!",
            first_name="Laura",
        )
        self.url = reverse("usuarios:perfil")

    def test_usuario_anonimo_no_puede_modificar_datos(self):
        response = self.client.post(
            self.url,
            {
                "first_name": "Modificado",
                "last_name": "Sin permiso",
                "email": "otro@example.com",
            },
        )

        self.assertRedirects(
            response,
            f"{reverse('usuarios:login')}?next={self.url}",
        )
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "Laura")
        self.assertEqual(self.user.email, "laura@example.com")
