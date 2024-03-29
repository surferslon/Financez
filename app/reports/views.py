import calendar
from datetime import date, datetime, timedelta

from accounts.models import Account, AccountBalance
from currencies.models import Currency
from django.db.models import F, Q, Sum
from django.http import HttpResponse, JsonResponse
from django.template.response import TemplateResponse
from django.views import View
from django.views.generic import TemplateView
from entries.models import Entry


def change_field(request):
    acc_pk = request.POST.get("acc_pk")
    acc_field = request.POST.get("acc_field")
    new_value = request.POST.get("value")
    update_params = {acc_field: new_value}
    Account.objects.filter(pk=acc_pk).update(**update_params)
    return HttpResponse("")


def append_missing_dates(results, group, period_from, period_to):
    iter_date = period_from
    while iter_date < period_to:
        group_date = "Total" if group else f"{iter_date.year}.{iter_date.month}"
        group_dict = next((item for item in results if item["group_date"] == group_date), None)
        if not group_dict:
            results.append({"group_date": group_date})
        if iter_date.month > 11:
            iter_date = iter_date.replace(year=iter_date.year + 1, month=1, day=1)
        else:
            iter_date = iter_date.replace(month=iter_date.month + 1, day=1)

    return results


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


class MainView(TemplateView):
    template_name = "reports/index.html"

    def get_context_data(self, **kwargs):
        context = super(MainView, self).get_context_data(**kwargs)
        today = datetime.now()
        user = self.request.user

        context["period_from"] = date(today.year, 1, 1).strftime("%Y-%m-%d")
        context["period_to"] = today.strftime("%Y-%m-%d")
        context["current_month"] = today
        context["current_cur"] = Currency.objects.get(user=user, selected=True)
        # results
        try:
            currency = Currency.objects.get(user=user, selected=True)
        except Currency.DoesNotExist:
            currency = None
        context["results_queryset"] = (
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

        context["result_types"] = {
            "assets": Account.RESULT_ASSETS,
            "debts": Account.RESULT_DEBTS,
            "plans": Account.RESULT_PLANS,
            "incomes": Account.RESULT_INCOMES,
            "expenses": Account.RESULT_EXPENSES,
        }
        return context


class ReportDataView(View):
    def _calculate_results(self, results, entries, group_by_parent, group_all):
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
                    acc_name = f"exp:{entr.acc_dr.parent.name}:{entr.acc_dr.name}" if entr.acc_dr.parent else f"exp:{entr.acc_dr.name}"
            else:
                acc_name = f"inc:{entr.acc_cr.name}"
            if group_dict := next((item for item in results if item["group_date"] == group_date), None):
                group_dict[acc_name] = entr.total + group_dict.get(acc_name, 0)
            else:
                results.append({"group_date": group_date, acc_name: entr.total})

    def get_income_accounts(self, qs_inc):
        return [f"inc:{acc}" for acc in set(qs_inc.values_list("acc_cr__name", flat=True))]

    def get_expenses_accounts(self, user, group_by_parent):
        return (
            [
                f'exp:{acc["name"]}'
                for acc in Account.objects.filter(results=Account.RESULT_EXPENSES, parent=None, user=user).order_by("order").values("name")
            ]
            if group_by_parent
            else [
                f'exp:{acc["parent__name"]}:{acc["name"]}'
                for acc in Account.objects.filter(results=Account.RESULT_EXPENSES, user=user).values("name", "parent__name").distinct()
            ]
        )

    def get(self, request, *args, **kwargs):
        today = datetime.now()
        group_by_parent = True
        group_all = request.GET.get("group_all") == "true"
        period_from = request.GET.get("period-from", date(today.year, 1, 1))
        period_to = request.GET.get("period-to", today)
        user = request.user
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
        self._calculate_results(results, qs_exp, group_by_parent, group_all)
        self._calculate_results(results, qs_inc, group_by_parent, group_all)
        inc_accounts = self.get_income_accounts(qs_inc)
        exp_accounts = self.get_expenses_accounts(user, group_by_parent)
        period_inc, period_exp, period_sum = get_period_results(period_from, period_to, user, currency)
        return JsonResponse(
            {
                "accounts_incomes": inc_accounts,
                "accounts_expenses": exp_accounts,
                "results": sorted(results, key=lambda k: k["group_date"]),
                "period_inc": period_inc,
                "period_exp": period_exp,
                "period_sum": period_sum,
            },
            safe=False,
        )


class ReportDetailsView(View):
    def _get_period_from(
        self,
        request,
    ):
        period_from = request.GET.get("period-from", date(datetime.now().year, 1, 1))
        if isinstance(period_from, str):
            try:
                period_from = datetime.strptime(period_from, "%Y-%m-%d")
            except ValueError:
                period_from = datetime.strptime(period_from, "%Y.%m")
        return period_from

    def _get_period_to(self, request):
        period_to = request.GET.get("period-to", datetime.now())
        if isinstance(period_to, str):
            try:
                period_to = datetime.strptime(period_to, "%Y-%m-%d")
            except ValueError:
                period_to = datetime.strptime(period_to, "%Y.%m")
                period_to = period_to.replace(day=calendar.monthrange(period_to.year, period_to.month)[1])
        period_to = period_to.replace(hour=23, minute=59)
        return period_to

    def get(self, request, *args, **kwargs):
        category = request.GET.get("category")
        results, category = category.split(":")
        try:
            parent_acc = Account.objects.get(name=category, results=results)
        except Account.DoesNotExist:
            parent_acc = Account.objects.get(name__contains=category, results=results)
        period_from = self._get_period_from(request)
        period_to = self._get_period_to(request)
        params = {
            "currency": Currency.objects.get(user=request.user, selected=True),
            "user": request.user,
            "date__gte": period_from,
            "date__lte": period_to,
        }
        if results == "exp":
            qs = Entry.objects.filter(Q(acc_dr__parent=parent_acc) | Q(acc_dr=parent_acc), **params).annotate(
                acc_name=F("acc_dr__name"), acc_id=F("acc_dr__id")
            )
        else:
            qs = Entry.objects.filter(Q(acc_cr__parent=parent_acc) | Q(acc_cr=parent_acc), **params).annotate(
                acc_name=F("acc_cr__name"), acc_id=F("acc_cr__id")
            )
        results = []
        accounts = []
        group = request.GET.get("group_details") == "true"
        iter_date = period_from
        while iter_date < period_to:
            group_date = "Total" if group else f"{iter_date.year}.{iter_date.month}"
            group_dict = next((item for item in results if item["group_date"] == group_date), None)
            if not group_dict:
                results.append({"group_date": group_date})
            if iter_date.month > 11:
                iter_date = iter_date.replace(year=iter_date.year + 1, month=1, day=1)
            else:
                iter_date = iter_date.replace(month=iter_date.month + 1, day=1)
        for entry in qs:
            group_date = "Total" if group else f"{entry.date.year}.{entry.date.month}"
            group_dict = next((item for item in results if item["group_date"] == group_date), None)
            group_dict[entry.acc_id] = entry.total + group_dict.get(entry.acc_id, 0)
            if entry.acc_id not in accounts:
                accounts.append(entry.acc_id)
        accounts = [{"valueField": acc.id, "name": acc.name} for acc in Account.objects.filter(id__in=accounts).order_by("order")]
        return JsonResponse(
            {"title": parent_acc.name, "results": results, "accounts": accounts},
            safe=False,
        )


class ReportEntriesView(View):
    def get(self, request, *args, **kwargs):
        acc_id = request.GET.get("acc_id")
        acc = Account.objects.get(id=acc_id)
        today = datetime.now()
        month = request.GET.get("month", None)
        params = {
            "currency": Currency.objects.get(user=request.user, selected=True),
            "user": request.user,
        }
        if month:
            year, month = month.split(".")
            params["date__gte"] = date(year=int(year), month=int(month), day=1)
            if int(month) > 11:
                params["date__lte"] = date(year=int(year) + 1, month=1, day=1) - timedelta(days=1)
            else:
                params["date__lte"] = date(year=int(year), month=int(month) + 1, day=1) - timedelta(days=1)
        else:
            self._set_time_period(request, today, params)
        qs = Entry.objects.filter(Q(acc_cr=acc) | Q(acc_dr=acc), **params).order_by("-date")
        return TemplateResponse(
            request,
            "reports/report_entries.html",
            {"entries": qs, "total_sum": qs.aggregate(Sum("total"))["total__sum"]},
        )

    def _set_time_period(self, request, today, params):
        period_from = request.GET.get("period-from", date(today.year, 1, 1))
        period_to = request.GET.get("period-to", today)
        if isinstance(period_from, str):
            period_from = datetime.strptime(period_from, "%Y-%m-%d")
        if isinstance(period_to, str):
            period_to = datetime.strptime(period_to, "%Y-%m-%d")
        params["date__gte"] = period_from
        params["date__lte"] = period_to
