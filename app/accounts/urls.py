from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [path("list/", views.AccountListView().as_view(), name="account_list")]