from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect, render
from django.urls import reverse_lazy

from .forms import LoginForm, PerfilForm, RegistroForm


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


@login_required
def perfil(request):
    if request.method == "POST":
        form = PerfilForm(request.POST, instance=request.user)

        if form.is_valid():
            form.save()
            messages.success(request, "Tus datos se actualizaron correctamente.")
            return redirect("usuarios:perfil")
    else:
        form = PerfilForm(instance=request.user)

    return render(request, "usuarios/perfil.html", {"form": form})
