from django.views.generic import TemplateView
from datetime import date, datetime
from django.db.models import Q
from currencies.models import Currency
from accounts.models import Account, AccountBalance


class MainView(TemplateView):
    template_name = "reports/index.html"

    def _get_user_currency(self, user):
        try:
            return Currency.objects.get(user=user, selected=True)
        except Currency.DoesNotExist:
            return None

    def _get_accounts_balances(self, user, currency):
        return (
            AccountBalance.objects.filter(
                Q(acc__results=Account.RESULT_ASSETS) | Q(acc__results=Account.RESULT_PLANS) | Q(acc__results=Account.RESULT_DEBTS),
                currency=currency,
                acc__user=user,
            )
            .exclude(total=0)
            .values("acc__name", "acc__results", "total", "acc__parent__name", "acc__parent__order")
            .order_by("acc__order")
        )

    def _get_period_filter(self, context):
        today = datetime.now()
        context["period_from"] = date(today.year, 1, 1).strftime("%Y-%m-%d")
        context["period_to"] = today.strftime("%Y-%m-%d")
        context["current_month"] = today

    def get_context_data(self, **kwargs):
        context = super(MainView, self).get_context_data(**kwargs)
        user = self.request.user
        currency = self._get_user_currency(user)
        self._get_period_filter(context)
        context["current_cur"] = currency
        context["results_queryset"] = self._get_accounts_balances(user, currency)
        context["result_types"] = {
            "assets": Account.RESULT_ASSETS,
            "debts": Account.RESULT_DEBTS,
            "plans": Account.RESULT_PLANS,
            "incomes": Account.RESULT_INCOMES,
            "expenses": Account.RESULT_EXPENSES,
        }
        return context
