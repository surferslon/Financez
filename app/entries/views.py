import calendar
from datetime import date, datetime, timedelta

from django.db.models import F, Q, Sum
from entries.serializers import EntryCreateSerializer, EntrySerializer
from financez.models import Account, Currency, Entry
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView


class ReportDataView(APIView):
    def calculate_results(self, results, entries, group_all):
        for entr in entries:
            if group_all:
                group_date = "Total"
            else:
                month = entr.date.strftime("%m")
                group_date = f"{entr.date.year}.{month}"
            if entr.acc_dr.results == Account.RESULT_EXPENSES:
                acc_name = entr.acc_dr.parent.id if entr.acc_dr.parent else entr.acc_dr.id
            else:
                acc_name = entr.acc_cr.id
            if group_dict := next((item for item in results if item["group_date"] == group_date), None):
                group_dict[acc_name] = entr.total + group_dict.get(acc_name, 0)
            else:
                results.append({"group_date": group_date, acc_name: entr.total})

    def get_income_accounts(self, qs_inc):
        return [
            {"name": f"inc:{acc.name}", "id": acc.id}
            for acc in Account.objects.filter(id__in=set(qs_inc.values_list("acc_cr__id", flat=True)))
        ]

    def get_expenses_accounts(self, user, group_by_parent):
        return (
            [
                {"name": f"exp:{acc['name']}", "id": acc["id"]}
                for acc in Account.objects.filter(results=Account.RESULT_EXPENSES, parent=None, user=user)
                .order_by("order")
                .values("name", "id")
            ]
            if group_by_parent
            else [
                {"name": f'exp:{acc["parent__name"]}:{acc["name"]}', "id": acc["id"]}
                for acc in Account.objects.filter(results=Account.RESULT_EXPENSES, user=user)
                .values("name", "parent__name", "id")
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
        self.calculate_results(results, qs_exp, group_all)
        self.calculate_results(results, qs_inc, group_all)
        inc_accounts = self.get_income_accounts(qs_inc)
        exp_accounts = self.get_expenses_accounts(user, group_by_parent)
        return Response(
            {
                "accounts_incomes": inc_accounts,
                "accounts_expenses": exp_accounts,
                "results": sorted(results, key=lambda k: k["group_date"]),
            },
        )


class ReportDetailsView(APIView):
    def _get_period_from(self, request):
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
        acc_id = kwargs["acc_id"]
        parent_acc = Account.objects.get(id=acc_id)
        res_type = parent_acc.results
        period_from = self._get_period_from(request)
        period_to = self._get_period_to(request)
        params = {
            "currency": Currency.objects.get(user=request.user, selected=True),
            "user": request.user,
            "date__gte": period_from,
            "date__lte": period_to,
        }
        if res_type == "exp":
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
        accounts = [
            {"valueField": acc.id, "name": acc.name}
            for acc in Account.objects.filter(id__in=accounts).order_by("order")
        ]
        return Response({"title": parent_acc.name, "results": results, "accounts": accounts})


class AccEntriesView(APIView):
    def get(self, request, *args, **kwargs):
        acc_id = kwargs.get("acc_id")
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
            period_from = request.GET.get("period-from", date(today.year, 1, 1))
            period_to = request.GET.get("period-to", today)
            if isinstance(period_from, str):
                period_from = datetime.strptime(period_from, "%Y-%m-%d")
            if isinstance(period_to, str):
                period_to = datetime.strptime(period_to, "%Y-%m-%d")
            params["date__gte"] = period_from
            params["date__lte"] = period_to
        qs = Entry.objects.filter(Q(acc_cr=acc) | Q(acc_dr=acc), **params).order_by("-date")
        return Response(
            {"entries": qs.values("date", "total", "comment"), "total_sum": qs.aggregate(Sum("total"))["total__sum"]}
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
            Entry.objects.filter(date__gte=date_from, date__lte=date_to, currency=currency, user=user)
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
