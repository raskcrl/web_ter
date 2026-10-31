from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

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
