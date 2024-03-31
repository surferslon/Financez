from datetime import date, datetime

from accounts.models import Currency
from django.views.generic import CreateView
from entries.forms import NewEntryForm
from entries.models import Entry


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
        context["date_from"] = date_from
        context["date_to"] = date_to
        return context
