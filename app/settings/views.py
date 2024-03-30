from accounts.forms import NewAccForm
from accounts.models import Account
from accounts.utils import make_account_tree
from currencies.forms import NewCurForm
from currencies.models import Currency
from django.http import HttpResponse
from django.views.generic import TemplateView


class SettingsView(TemplateView):
    template_name = "settings/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        section = kwargs.get("section")
        user = self.request.user
        context["current_cur"] = Currency.objects.get(user=user, selected=True)
        if section == "general":
            context["currencies"] = Currency.objects.filter(user=user)
            context["new_cur_form"] = NewCurForm
        context["account_list"] = make_account_tree(user, section)
        context["available_parents"] = Account.objects.filter(results=section, parent=None, user=user).values("pk", "name")
        context["new_acc_form"] = NewAccForm(section=section, user=user)
        context["sections"] = {
            "general": "general",
            "assets": Account.RESULT_ASSETS,
            "plans": Account.RESULT_PLANS,
            "debts": Account.RESULT_DEBTS,
            "incomes": Account.RESULT_INCOMES,
            "expenses": Account.RESULT_EXPENSES,
        }
        return context


def change_field(request):
    acc_pk = request.POST.get("acc_pk")
    acc_field = request.POST.get("acc_field")
    new_value = request.POST.get("value")
    update_params = {acc_field: new_value}
    Account.objects.filter(pk=acc_pk).update(**update_params)
    return HttpResponse("")


def change_currency(request):
    currency = Currency.objects.get(user=request.user, pk=request.POST.get("cur_pk"))
    currency.selected = True
    currency.save()
    return HttpResponse("")
