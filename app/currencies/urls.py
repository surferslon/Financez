from currencies import views
from django.urls import path

app_name = "currencies"

urlpatterns = [
    path("list/", views.CurrenciesListView.as_view(), name="currencies_list"),
    path("set/<int:pk>", views.CurrenciesSetView.as_view(), name="set_currency"),
]
