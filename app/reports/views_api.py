from datetime import date, datetime

from accounts.models import Account
from currencies.models import Currency
from django.db.models import Q, Sum
from django.template.response import TemplateResponse
from django.views import View
from entries.models import Entry
from reports.services import ChartAccDetails, ChartDataAggregator
from reports.utils import parse_dates
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
        aggregator.aggregate()
        return Response(aggregator.dict())


class ReportDetailsView(APIView):
    acc_aggregator = ChartAccDetails

    def get(self, request):
        acc_id = request.GET.get("accId")
        period = request.GET.get("period")
        period_from, period_to = parse_dates(period)
        aggr = self.acc_aggregator(request.user, acc_id, period_from, period_to)
        aggr.aggregate()
        return TemplateResponse(request, 'reports/details.html', {'results': aggr.results, 'total': aggr.total, 'period': period})


class ReportEntriesView(View):
    def get(self, request, *args, **kwargs):
        acc_id = request.GET.get("accid")
        acc = Account.objects.get(id=acc_id)
        period_from, period_to = parse_dates(request.GET.get("period"))
        params = {
            "currency": Currency.objects.get(user=request.user, selected=True),
            "user": request.user,
            'date__gte': period_from,
            'date__lt': period_to,
        }
        qs = Entry.objects.filter(Q(acc_cr=acc) | Q(acc_dr=acc), **params).order_by("-date")
        return TemplateResponse(
            request,
            "reports/entries.html",
            {"entries": qs, "total_sum": qs.aggregate(Sum("total"))["total__sum"]},
        )
