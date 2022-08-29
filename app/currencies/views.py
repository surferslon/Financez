from currencies.serializers import CurrencySerializer
from financez.models import Currency
from rest_framework.generics import ListAPIView, UpdateAPIView
from rest_framework.views import APIView


class CurrenciesListView(ListAPIView):
    serializer_class = CurrencySerializer

    def get_queryset(self):
        return Currency.objects.filter(user=self.request.user)


class CurrenciesSetView(UpdateAPIView):
    serializer_class = CurrencySerializer
    queryset = Currency.objects.all()
