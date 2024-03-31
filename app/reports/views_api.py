import calendar
from datetime import date, datetime, timedelta

from accounts.models import Account
from currencies.models import Currency
from django.db.models import F, Q, Sum
from django.template.response import TemplateResponse
from django.views import View
from entries.models import Entry
from reports.services import ChartDataAggregator
from rest_framework.response import Response
from rest_framework.views import APIView


class ReportDataView(APIView):
    aggregator_class = ChartDataAggregator

    def _clean_period_filters(self, request):
        today = datetime.now()
        period_from = request.GET.get("period-from", date(today.year, 1, 1))
        period_to = request.GET.get("period-to", today)
        if isinstance(period_from, str):
            period_from = datetime.strptime(period_from, "%Y-%m-%d")
        if isinstance(period_to, str):
            period_to = datetime.strptime(period_to, "%Y-%m-%d")
        return period_from, period_to

    def _get_user_currency(self, user):
        try:
            return Currency.objects.get(user=user, selected=True)
        except Currency.DoesNotExist:
            return None

    def get(self, request):
        period_from, period_to = self._clean_period_filters(request)
        user = request.user
        currency = self._get_user_currency(user)
        aggregator = self.aggregator_class(
            user, currency, period_from, period_to, group_by_parent=True, group_all=request.GET.get("group_all") == "true"
        )
        return Response(aggregator.dict())


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

    def get(self, request):
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
        return Response({"title": parent_acc.name, "results": results, "accounts": accounts})


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
