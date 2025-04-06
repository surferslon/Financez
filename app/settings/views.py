from accounts.forms import NewAccForm
from accounts.models import Account
from accounts.utils import make_account_tree
from currencies.forms import NewCurForm
from currencies.models import Currency
from django.views.generic import TemplateView


class SettingsView(TemplateView):
    template_name = "settings/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        section = kwargs.get("section")
        user = self.request.user
        context["current_cur"] = Currency.objects.get(user=user, selected=True)
        context["currencies"] = Currency.objects.filter(user=user)
        context["new_cur_form"] = NewCurForm
        context["account_list"] = make_account_tree(user, section)
        context["available_parents"] = Account.objects.filter(results=section, parent=None, user=user).values("pk", "name")
        context["new_acc_form"] = NewAccForm(section=section, user=user)
        return context
