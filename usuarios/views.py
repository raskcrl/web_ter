from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.core.files.storage import default_storage
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache

from .forms import (
    CambioPasswordForm,
    FotoPerfilForm,
    LoginForm,
    PerfilForm,
    RegistroForm,
)
from .models import PerfilUsuario


def registro(request):
    if request.user.is_authenticated:
        return redirect("usuarios:perfil")

    if request.method == "POST":
        form = RegistroForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(
                request,
                user,
                backend="django.contrib.auth.backends.ModelBackend",
            )
            messages.success(
                request,
                "Tu cuenta fue creada correctamente. ¡Bienvenido a Web Ter!",
            )
            return redirect("usuarios:perfil")
    else:
        form = RegistroForm()

    return render(request, "usuarios/registro.html", {"form": form})


class IniciarSesionView(LoginView):
    template_name = "usuarios/login.html"
    authentication_form = LoginForm
    redirect_authenticated_user = True

    def form_valid(self, form):
        messages.success(
            self.request,
            f"Bienvenido de nuevo, {form.get_user().get_username()}.",
        )
        return super().form_valid(form)


class CerrarSesionView(LogoutView):
    next_page = reverse_lazy("inicio")


@never_cache
@login_required
def perfil(request):
    perfil_usuario = PerfilUsuario.objects.filter(usuario=request.user).first()

    if request.method == "POST":
        form = PerfilForm(request.POST, instance=request.user)

        if form.is_valid():
            form.save()
            messages.success(request, "Tus datos se actualizaron correctamente.")
            return redirect("usuarios:perfil")
    else:
        form = PerfilForm(instance=request.user)

    return render(
        request,
        "usuarios/perfil.html",
        {
            "form": form,
            "foto_form": FotoPerfilForm(instance=perfil_usuario),
            "perfil": perfil_usuario,
        },
    )


@never_cache
@login_required
def perfil_foto(request):
    if request.method != "POST":
        return redirect("usuarios:perfil")

    perfil_usuario = PerfilUsuario.objects.filter(usuario=request.user).first()
    foto_anterior = (
        perfil_usuario.foto.name
        if perfil_usuario and perfil_usuario.foto
        else None
    )

    form = FotoPerfilForm(
        request.POST,
        request.FILES,
        instance=perfil_usuario,
    )

    if form.is_valid():
        perfil_usuario = form.save(commit=False)
        perfil_usuario.usuario = request.user

        eliminar_foto = form.cleaned_data.get("eliminar_foto")
        nueva_foto = form.cleaned_data.get("foto")

        if eliminar_foto:
            perfil_usuario.foto = None

        perfil_usuario.save()

        if foto_anterior and (eliminar_foto or nueva_foto):
            default_storage.delete(foto_anterior)

        if eliminar_foto:
            messages.success(
                request,
                "Tu foto de perfil se eliminó correctamente.",
            )
        else:
            messages.success(
                request,
                "Tu foto de perfil se actualizó correctamente.",
            )

        return redirect("usuarios:perfil")

    return render(
        request,
        "usuarios/perfil.html",
        {
            "form": PerfilForm(instance=request.user),
            "foto_form": form,
            "perfil": perfil_usuario,
        },
    )


@method_decorator(never_cache, name="dispatch")
class CambioPasswordView(PasswordChangeView):
    template_name = "usuarios/password_change.html"
    form_class = CambioPasswordForm
    success_url = reverse_lazy("usuarios:perfil")

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            "Tu contraseña se actualizó correctamente.",
        )
        return response
