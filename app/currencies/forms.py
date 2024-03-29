from currencies.models import Currency
from django import forms
from django.utils.translation import gettext as _


class NewCurForm(forms.ModelForm):
    class Meta:
        model = Currency
        fields = ["name"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["name"].label = _("Name")
