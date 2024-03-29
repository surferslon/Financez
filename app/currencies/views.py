from currencies.forms import NewCurForm
from currencies.models import Currency
from currencies.serializers import CurrencySerializer
from django.urls import reverse
from django.views.generic import CreateView
from rest_framework.generics import ListAPIView, UpdateAPIView


class CurrenciesListView(ListAPIView):
    serializer_class = CurrencySerializer

    def get_queryset(self):
        return Currency.objects.filter(user=self.request.user)


class CurrenciesSetView(UpdateAPIView):
    serializer_class = CurrencySerializer
    queryset = Currency.objects.all()


class NewCurView(CreateView):
    model = Currency
    form_class = NewCurForm

    def form_valid(self, form):
        user = self.request.user
        form.instance.user = user
        if not Currency.objects.filter(user=user).exists():
            form.instance.selected = True
        return super().form_valid(form)

    def get_success_url(self, **kwargs):
        return reverse("settings", args=("general",))
