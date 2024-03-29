from accounts.models import Account
from django import forms
from django.utils.translation import gettext as _


class NewAccForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ["name", "acc_type", "results", "order", "parent"]

    def __init__(self, *args, **kwargs):
        section = kwargs.pop("section", None)
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        if not section:
            return
        self.fields["parent"].queryset = Account.objects.filter(results=section, parent=None, user=user)
        self.fields["results"].initial = section
        if section in (
            Account.RESULT_ASSETS,
            Account.RESULT_PLANS,
            Account.RESULT_EXPENSES,
        ):
            self.fields["acc_type"].initial = Account.TYPE_ACTIVE
        else:
            self.fields["acc_type"].initial = Account.TYPE_PASSIVE
        self.fields["name"].label = _("Name")
        self.fields["acc_type"].label = _("Type")
        self.fields["results"].label = _("Results")
        self.fields["order"].label = _("Order")
        self.fields["parent"].label = _("Parent")
