from django import forms
from django.db.models import Max

from ejercicios.models import Categoria, Ejercicio
from rutinas.models import Rutina, RutinaEjercicio


def _aplicar_estilos(form):
    for field in form.fields.values():
        widget = field.widget

        if isinstance(widget, forms.CheckboxInput):
            widget.attrs.setdefault("class", "form-checkbox")
            continue

        clases = widget.attrs.get("class", "")
        if "form-input" not in clases.split():
            widget.attrs["class"] = f"{clases} form-input".strip()


class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ("nombre", "descripcion", "activa", "orden")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _aplicar_estilos(self)


class EjercicioForm(forms.ModelForm):
    class Meta:
        model = Ejercicio
        fields = (
            "categoria",
            "nombre",
            "descripcion",
            "instrucciones",
            "dificultad",
            "duracion_minutos",
            "imagen",
            "video_url",
            "activo",
        )
        widgets = {
            "imagen": forms.ClearableFileInput(
                attrs={"accept": "image/jpeg,image/png,image/webp"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _aplicar_estilos(self)
        self.fields["duracion_minutos"].min_value = 1


class RutinaForm(forms.ModelForm):
    class Meta:
        model = Rutina
        fields = ("nombre", "descripcion", "objetivo", "activa", "orden")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _aplicar_estilos(self)


class RutinaEjercicioForm(forms.ModelForm):
    class Meta:
        model = RutinaEjercicio
        fields = ("ejercicio", "orden", "notas")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _aplicar_estilos(self)

        if self.instance.pk is None and not self.is_bound:
            self.fields["orden"].initial = self._siguiente_orden()

    def _siguiente_orden(self):
        if not self.instance.rutina_id:
            return 1

        ultimo = RutinaEjercicio.objects.filter(
            rutina_id=self.instance.rutina_id
        ).aggregate(Max("orden"))["orden__max"]

        return (ultimo or 0) + 1

    def clean(self):
        cleaned_data = super().clean()
        ejercicio = cleaned_data.get("ejercicio")

        if not ejercicio or not self.instance.rutina_id:
            return cleaned_data

        asociaciones = RutinaEjercicio.objects.filter(
            rutina_id=self.instance.rutina_id,
            ejercicio=ejercicio,
        )

        if self.instance.pk:
            asociaciones = asociaciones.exclude(pk=self.instance.pk)

        if asociaciones.exists():
            self.add_error(
                "ejercicio",
                "Este ejercicio ya forma parte de la rutina.",
            )

        return cleaned_data
