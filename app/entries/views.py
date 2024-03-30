from datetime import date, datetime

from accounts.models import Account, Currency
from accounts.utils import make_account_tree
from django.views.generic import CreateView
from entries.forms import NewEntryForm
from entries.models import Entry
from entries.serializers import EntryCreateSerializer, EntrySerializer
from rest_framework.generics import CreateAPIView, ListAPIView


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


class EntriesView(CreateView):
    model = Entry
    template_name = "entries/index.html"
    form_class = NewEntryForm
    success_url = "/entries"

    def form_valid(self, form):
        user = self.request.user
        form.instance.user = user
        form.instance.currency_id = Currency.objects.get(user=user, selected=True).id
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = datetime.now()
        user = self.request.user
        date_from = self.request.GET.get("date-from") or date(today.year, today.month, 1).strftime("%Y-%m-%d")
        date_to = self.request.GET.get("date-to") or today.strftime("%Y-%m-%d")
        context["current_cur"] = Currency.objects.get(user=user, selected=True)
        context["result_types"] = {
            "assets": Account.RESULT_ASSETS,
            "debts": Account.RESULT_DEBTS,
            "plans": Account.RESULT_PLANS,
            "incomes": Account.RESULT_INCOMES,
            "expenses": Account.RESULT_EXPENSES,
        }
        try:
            currency = Currency.objects.get(user=user, selected=True)
        except Currency.DoesNotExist:
            currency = None
        context["current_month"] = today
        # entries per month
        context["entries"] = (
            Entry.objects.order_by("-date")
            .filter(date__gte=date_from, date__lte=date_to, currency=currency, user=user)
            .values("date", "acc_dr__name", "acc_cr__name", "total", "comment", "acc_cr__results")
        )
        # accounts
        context["account_list"] = make_account_tree(user)
        context["date_from"] = date_from
        context["date_to"] = date_to
        return context
