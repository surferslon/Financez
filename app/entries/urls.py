from django.urls import path
from django.contrib.auth.decorators import login_required

from entries import views

app_name = "entries"

urlpatterns = [
    path("index/", login_required(views.EntriesView.as_view()), name="index"),
    path("list/", login_required(views.EntriesListView.as_view()), name="entries_list"),
    path("create/", login_required(views.EntryCreateView.as_view()), name="entries_create"),
]
