from datetime import date, datetime

from django.db.models import Sum
from entries.serializers import EntryCreateSerializer, EntrySerializer
from financez.models import Account, Currency, Entry
from rest_framework.generics import CreateAPIView, ListAPIView
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
    return f"{inc_sum:.3f}", f"{exp_sum:.3f}", f"{res_sum:.3f}"


class ReportDataView(APIView):
    def calculate_results(self, results, entries, group_by_parent, group_all):
        for entr in entries:
            if group_all:
                group_date = "Total"
            else:
                month = entr.date.strftime("%m")
                group_date = f"{entr.date.year}.{month}"
            if entr.acc_dr.results == Account.RESULT_EXPENSES:
                if group_by_parent:
                    acc_name = f"exp:{entr.acc_dr.parent.name}" if entr.acc_dr.parent else f"exp:{entr.acc_dr.name}"
                else:
                    acc_name = (
                        f"exp:{entr.acc_dr.parent.name}:{entr.acc_dr.name}"
                        if entr.acc_dr.parent
                        else f"exp:{entr.acc_dr.name}"
                    )
            else:
                acc_name = f"inc:{entr.acc_cr.name}"
            group_dict = next((item for item in results if item["group_date"] == group_date), None)
            if group_dict:
                group_dict[acc_name] = entr.total + group_dict.get(acc_name, 0)
            else:
                results.append({"group_date": group_date, acc_name: entr.total})

    def get_income_accounts(self, qs_inc):
        return [f"inc:{acc}" for acc in set(qs_inc.values_list("acc_cr__name", flat=True))]

    def get_expenses_accounts(self, user, group_by_parent):
        return (
            [
                f'exp:{acc["name"]}'
                for acc in Account.objects.filter(results=Account.RESULT_EXPENSES, parent=None, user=user)
                .order_by("order")
                .values("name")
            ]
            if group_by_parent
            else [
                f'exp:{acc["parent__name"]}:{acc["name"]}'
                for acc in Account.objects.filter(results=Account.RESULT_EXPENSES, user=user)
                .values("name", "parent__name")
                .distinct()
            ]
        )

    def get(self, request, *args, **kwargs):
        today = datetime.now()
        group_by_parent = True
        group_all = request.GET.get("group_all") == "true"
        period_from = request.GET.get("period-from", date(today.year, 1, 1))
        period_to = request.GET.get("period-to", today)
        user = request.user
        print(user)
        try:
            currency = Currency.objects.get(user=user, selected=True)
        except Currency.DoesNotExist:
            currency = None
        if isinstance(period_from, str):
            period_from = datetime.strptime(period_from, "%Y-%m-%d")
        if isinstance(period_to, str):
            period_to = datetime.strptime(period_to, "%Y-%m-%d")
        qs_exp = (
            Entry.objects.filter(
                date__gte=period_from,
                date__lte=period_to,
                user=user,
                acc_dr__results=Account.RESULT_EXPENSES,
                currency=currency,
            )
            .select_related("acc_dr", "acc_dr__parent")
            .order_by("date")
        )
        qs_inc = (
            Entry.objects.filter(
                date__gte=period_from,
                date__lte=period_to,
                user=user,
                acc_cr__results=Account.RESULT_INCOMES,
                currency=currency,
            )
            .select_related("acc_cr", "acc_cr__parent")
            .order_by("date")
        )
        results = []
        self.calculate_results(results, qs_exp, group_by_parent, group_all)
        self.calculate_results(results, qs_inc, group_by_parent, group_all)
        inc_accounts = self.get_income_accounts(qs_inc)
        exp_accounts = self.get_expenses_accounts(user, group_by_parent)
        period_inc, period_exp, period_sum = get_period_results(period_from, period_to, user, currency)
        return Response(
            {
                "accounts_incomes": inc_accounts,
                "accounts_expenses": exp_accounts,
                "results": sorted(results, key=lambda k: k["group_date"]),
                "period_inc": period_inc,
                "period_exp": period_exp,
                "period_sum": period_sum,
            },
        )


class EntriesListView(ListAPIView):
    serializer_class = EntrySerializer

    def get_queryset(self):
        today = datetime.now()
        user = self.request.user
        currency = Currency.objects.get(user=user, selected=True)
        date_from = self.request.GET.get("date-from") or date(today.year, today.month, 1).strftime("%Y-%m-%d")
        date_to = self.request.GET.get("date-to") or today.strftime("%Y-%m-%d")
        return (
            Entry.objects
            .filter(date__gte=date_from, date__lte=date_to, currency=currency, user=user)
            .values("id", "date", "acc_dr__name", "acc_cr__name", "total", "comment", "acc_cr__results")
            .order_by("-date", "-id")
        )


class EntryCreateView(CreateAPIView):
    serializer_class = EntryCreateSerializer

    def get_serializer(self, data):
        user = self.request.user
        data["user"] = user.id
        data["currency"] = Currency.objects.get(user=user, selected=True).id
        return super().get_serializer(data=data)
