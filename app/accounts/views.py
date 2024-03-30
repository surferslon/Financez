from collections import defaultdict
from datetime import date, datetime

from accounts.forms import NewAccForm
from accounts.models import Account, AccountBalance
from currencies.models import Currency
from django.db.models import F, Q, Sum
from django.urls import reverse
from django.views.generic import CreateView, DeleteView
from entries.models import Entry
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView


def get_period_results(date_from, date_to, user, currency):
    incomes_sum = (
        Entry.objects.filter(
            date__gte=date_from,
            date__lte=date_to,
            user=user,
            acc_cr__results=Account.RESULT_INCOMES,
            currency=currency,
        )
        .values("total")
        .aggregate(sum=Sum("total"))["sum"]
        or 0
    )
    expenses_sum = (
        Entry.objects.filter(
            date__gte=date_from,
            date__lte=date_to,
            user=user,
            acc_dr__results=Account.RESULT_EXPENSES,
            currency=currency,
        )
        .values("total")
        .aggregate(sum=Sum("total"))["sum"]
        or 0
    )
    inc_sum = round(incomes_sum, 3)
    exp_sum = round(expenses_sum, 3)
    res_sum = round(incomes_sum - expenses_sum, 3)
    return {"incomes": f"{inc_sum:.3f}", "expenses": f"{exp_sum:.3f}", "result": f"{res_sum:.3f}"}


class DelAccView(DeleteView):
    model = Account

    def get_success_url(self, **kwargs):
        return reverse("settings", args=(self.request.POST.get("section"),))


class NewAccView(CreateView):
    model = Account
    form_class = NewAccForm

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self, **kwargs):
        return reverse("settings", args=(self.request.POST.get("results"),))


class AccountListView(ListAPIView):
    def add_subaccounts(self, acc_list, filtered_list):
        result_tree = []
        for acc in filtered_list:
            parent_id = acc["pk"]
            if subaccounts := list(filter(lambda x: x["parent_id"] == parent_id, acc_list)):
                acc["subaccs"] = subaccounts
                for subacc in subaccounts:
                    subacc["subaccs"] = self.add_subaccounts(acc_list, filter(lambda x: x["parent_id"] == subacc["pk"], acc_list))
            result_tree.append(acc)
        return result_tree

    def make_account_tree(self, user, section=None):
        if section:
            accounts = (
                Account.objects.filter(results=section, user=user)
                .values("pk", "parent_id", "name", "order", "acc_type", "results")
                .order_by("order")
            )
        else:
            accounts = Account.objects.filter(user=user).values("pk", "parent_id", "name", "order", "results").order_by("order")
        acc_list = list(accounts)
        return self.add_subaccounts(acc_list, filter(lambda x: x["parent_id"] is None, acc_list))

    def get(self, request):
        # whats a crap
        user = request.user
        account_list = self.make_account_tree(user)
        categorized_dict = {
            "assets": [acc for acc in account_list if acc["results"] == "ast"],
            "expenses": [acc for acc in account_list if acc["results"] == "exp"],
            "plans": [acc for acc in account_list if acc["results"] == "pln"],
            "incomes": [acc for acc in account_list if acc["results"] == "inc"],
            "debts": [acc for acc in account_list if acc["results"] == "dbt"],
        }
        return Response(categorized_dict)


class ResultsView(APIView):
    def get(self, request):
        user = request.user
        currency = Currency.objects.get(user=user, selected=True)
        res = (
            AccountBalance.objects.filter(
                Q(acc__results=Account.RESULT_ASSETS) | Q(acc__results=Account.RESULT_PLANS) | Q(acc__results=Account.RESULT_DEBTS),
                currency=currency,
                acc__user=user,
            )
            .exclude(total=0)
            .values(
                "acc__name",
                "acc__results",
                "total",
                "acc__parent__name",
                "acc__parent__order",
            )
            .order_by("acc__order")
        )

        today = datetime.now()
        period_from = request.GET.get("period-from", date(today.year, 1, 1))
        period_to = request.GET.get("period-to", today)
        if isinstance(period_from, str):
            period_from = datetime.strptime(period_from, "%Y-%m-%d")
        if isinstance(period_to, str):
            period_to = datetime.strptime(period_to, "%Y-%m-%d")
        resp_dict = defaultdict(list)
        resp_dict["period_results"] = get_period_results(period_from, period_to, user, currency)
        for row in res:
            resp_dict[row["acc__results"]].append(
                {
                    "name": (f"{row['acc__parent__name']}: {row['acc__name']}" if row["acc__parent__name"] else row["acc__name"]),
                    "sum": f"{row['total']:.3f}",
                }
            )

        return Response(resp_dict)
