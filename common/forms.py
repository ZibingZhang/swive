from django.forms import BaseForm as _BaseForm
from django.forms import Form, ModelForm, widgets


class BaseForm(Form):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        _bs5_process_fields(self)


class BaseModelForm(ModelForm):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        _bs5_process_fields(self)


def _bs5_process_fields(form: _BaseForm) -> None:
    for widget in map(lambda field: field.widget, form.fields.values()):
        if isinstance(widget, widgets.Select):
            widget.attrs["class"] = "form-select"
        elif isinstance(widget, widgets.TextInput):
            widget.attrs["class"] = "form-control"
