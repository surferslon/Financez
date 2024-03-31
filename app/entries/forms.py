from django import forms
from django.utils import timezone
from entries.models import Entry


class DateInput(forms.DateInput):
    input_type = "date"


class NewEntryForm(forms.ModelForm):
    class Meta:
        model = Entry
        fields = ["date", "acc_dr", "acc_cr", "total", "comment", "currency"]
        widgets = {"date": DateInput}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["acc_dr"].widget.attrs.update({"hidden": ""})
        self.fields["acc_cr"].widget.attrs.update({"hidden": ""})
        self.fields["date"].initial = timezone.now()
        self.fields["currency"].required = False


class UpdateEntryForm(forms.ModelForm):
    acc_dr__name = forms.CharField(required=False)
    acc_cr__name = forms.CharField(required=False)

    class Meta:
        model = Entry
        fields = ["date", "acc_dr", "acc_cr", "total", "comment"]
        widgets = {"date": DateInput}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["acc_dr"].widget.attrs.update({"hidden": ""})
        self.fields["acc_cr"].widget.attrs.update({"hidden": ""})
        if kwargs.get("instance"):
            self.fields["acc_dr__name"].initial = kwargs["instance"].acc_dr.name
            self.fields["acc_cr__name"].initial = kwargs["instance"].acc_cr.name
