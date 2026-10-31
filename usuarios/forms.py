from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordChangeForm,
    UserCreationForm,
)

from .models import PerfilUsuario

User = get_user_model()


class RegistroForm(UserCreationForm):
    email = forms.EmailField(
        label="Correo electrónico",
        required=True,
        widget=forms.EmailInput(
            attrs={
                "class": "form-input",
                "autocomplete": "email",
                "placeholder": "tu@correo.com",
            }
        ),
    )

    error_messages = {
        **UserCreationForm.error_messages,
        "password_mismatch": "Las contraseñas no coinciden.",
    }

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.order_fields(("username", "email", "password1", "password2"))

        self.fields["username"].label = "Nombre de usuario"
        self.fields["username"].help_text = (
            "Máximo 150 caracteres. Puedes usar letras, números y @/./+/-/_."
        )
        self.fields["username"].widget.attrs.update(
            {
                "class": "form-input",
                "autocomplete": "username",
                "placeholder": "Elige un nombre de usuario",
            }
        )

        self.fields["password1"].label = "Contraseña"
        self.fields["password1"].help_text = (
            "Mínimo 8 caracteres. Evita contraseñas comunes o solo numéricas."
        )
        self.fields["password1"].widget.attrs.update(
            {
                "class": "form-input",
                "autocomplete": "new-password",
                "placeholder": "Crea una contraseña segura",
            }
        )

        self.fields["password2"].label = "Confirmar contraseña"
        self.fields["password2"].help_text = "Escribe nuevamente tu contraseña."
        self.fields["password2"].widget.attrs.update(
            {
                "class": "form-input",
                "autocomplete": "new-password",
                "placeholder": "Repite la contraseña",
            }
        )

    def clean_username(self):
        username = self.cleaned_data["username"].strip()

        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError(
                "Ya existe una cuenta con este nombre de usuario."
            )

        return username

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()

        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(
                "Ya existe una cuenta registrada con este correo electrónico."
            )

        return email


class LoginForm(AuthenticationForm):
    error_messages = {
        "invalid_login": (
            "Usuario o contraseña incorrectos. "
            "Verifica tus datos e inténtalo de nuevo."
        ),
        "inactive": "Esta cuenta está deshabilitada.",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["username"].label = "Nombre de usuario"
        self.fields["username"].widget.attrs.update(
            {
                "class": "form-input",
                "autocomplete": "username",
                "placeholder": "Tu nombre de usuario",
            }
        )

        self.fields["password"].label = "Contraseña"
        self.fields["password"].widget.attrs.update(
            {
                "class": "form-input",
                "autocomplete": "current-password",
                "placeholder": "Tu contraseña",
            }
        )


class PerfilForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "email")
        labels = {
            "first_name": "Nombre",
            "last_name": "Apellido",
            "email": "Correo electrónico",
        }
        widgets = {
            "first_name": forms.TextInput(
                attrs={
                    "class": "form-input",
                    "autocomplete": "given-name",
                    "placeholder": "Tu nombre",
                }
            ),
            "last_name": forms.TextInput(
                attrs={
                    "class": "form-input",
                    "autocomplete": "family-name",
                    "placeholder": "Tu apellido",
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "class": "form-input",
                    "autocomplete": "email",
                    "placeholder": "tu@correo.com",
                }
            ),
        }

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        usuarios_con_email = User.objects.filter(email__iexact=email)

        if self.instance.pk:
            usuarios_con_email = usuarios_con_email.exclude(pk=self.instance.pk)

        if usuarios_con_email.exists():
            raise forms.ValidationError(
                "Ya existe una cuenta registrada con este correo electrónico."
            )

        return email


class FotoPerfilForm(forms.ModelForm):
    eliminar_foto = forms.BooleanField(
        label="Eliminar foto actual",
        required=False,
        widget=forms.CheckboxInput(attrs={"class": "form-checkbox"}),
    )

    class Meta:
        model = PerfilUsuario
        fields = ("foto",)
        widgets = {
            "foto": forms.FileInput(
                attrs={
                    "class": "form-input",
                    "accept": "image/jpeg,image/png,image/webp",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["foto"].label = "Foto de perfil"
        self.fields["foto"].help_text = (
            "Formatos permitidos: JPG, JPEG, PNG o WEBP. Tamaño máximo: 5 MB."
        )

        tiene_foto_actual = bool(
            self.instance and self.instance.pk and self.instance.foto
        )

        if not tiene_foto_actual:
            self.fields.pop("eliminar_foto", None)

    def clean_foto(self):
        foto = self.cleaned_data.get("foto")

        if not self.files.get(self.add_prefix("foto")):
            return None

        return foto

    def clean(self):
        cleaned_data = super().clean()
        foto = cleaned_data.get("foto")
        eliminar_foto = cleaned_data.get("eliminar_foto")
        tiene_foto_actual = bool(
            self.instance and self.instance.pk and self.instance.foto
        )

        if foto and eliminar_foto:
            raise forms.ValidationError(
                "Elige entre subir una foto nueva o eliminar la actual."
            )

        if not foto and not eliminar_foto and not tiene_foto_actual:
            raise forms.ValidationError(
                "Selecciona una imagen para actualizar tu foto de perfil."
            )

        return cleaned_data


class CambioPasswordForm(PasswordChangeForm):
    error_messages = {
        **PasswordChangeForm.error_messages,
        "password_incorrect": "La contraseña actual no es correcta.",
        "password_mismatch": "Las contraseñas nuevas no coinciden.",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["old_password"].label = "Contraseña actual"
        self.fields["old_password"].widget.attrs.update(
            {
                "class": "form-input",
                "autocomplete": "current-password",
                "placeholder": "Tu contraseña actual",
            }
        )

        self.fields["new_password1"].label = "Nueva contraseña"
        self.fields["new_password1"].widget.attrs.update(
            {
                "class": "form-input",
                "autocomplete": "new-password",
                "placeholder": "Crea una contraseña segura",
            }
        )

        self.fields["new_password2"].label = "Confirmar nueva contraseña"
        self.fields["new_password2"].widget.attrs.update(
            {
                "class": "form-input",
                "autocomplete": "new-password",
                "placeholder": "Repite la nueva contraseña",
            }
        )
