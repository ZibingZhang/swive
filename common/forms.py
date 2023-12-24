from django.forms import Form, ModelForm


class BaseForm(Form):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)


class BaseModelForm(ModelForm):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
