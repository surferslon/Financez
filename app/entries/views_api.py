from datetime import date, datetime

from entries.serializers import EntryCreateSerializer, EntrySerializer
from django.views.generic import DetailView
from rest_framework.generics import CreateAPIView, ListAPIView, UpdateAPIView
from accounts.models import Currency
from entries.models import Entry


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
            .order_by("date", "id")
        )


class EntryCreateView(CreateAPIView):
    serializer_class = EntryCreateSerializer

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(user=user, currency=Currency.objects.get(user=user, selected=True))

    def create(self, *args, **kwargs):
        response = super().create(*args, **kwargs)
        instance = Entry.objects.get(id=response.data["id"])
        response.data["acc_dr__name"] = instance.acc_dr.name
        response.data["acc_cr__name"] = instance.acc_cr.name
        return response


class ModalReadEntryView(DetailView):
    template_name = "entries/modal_edit_entry.html"

    def get_queryset(self, *args, **kwargs):
        return Entry.objects.filter(user=self.request.user)


class EntryUpdateView(UpdateAPIView):
    serializer_class = EntryCreateSerializer

    def update(self, *args, **kwargs):
        response = super().update(*args, **kwargs)
        instance = Entry.objects.get(id=response.data["id"])
        response.data["acc_dr__name"] = instance.acc_dr.name
        response.data["acc_cr__name"] = instance.acc_cr.name
        return response

    def get_queryset(self, *args, **kwargs):
        return Entry.objects.filter(user=self.request.user)
