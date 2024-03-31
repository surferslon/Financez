from django.contrib.auth.decorators import login_required
from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("list/", views.AccountListView().as_view(), name="account_list"),
    path("results/", views.ResultsView().as_view(), name="resulsts"),
    path("api/modal_accounts_list/", login_required(views.ModalAccountsListView.as_view()), name="modal_accounts_list"),
]
