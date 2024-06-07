from accounts.models import Account
from currencies.models import Currency
from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(["POST"])
def change_field(request):
    acc_pk = request.POST.get("acc_pk")
    acc_field = request.POST.get("acc_field")
    new_value = request.POST.get("value")
    update_params = {acc_field: new_value}
    Account.objects.filter(pk=acc_pk).update(**update_params)
    return Response()


@api_view(["POST"])
def change_currency(request):
    currency = Currency.objects.get(user=request.user, pk=request.POST.get("cur_pk"))
    currency.selected = True
    currency.save()
    return Response()
