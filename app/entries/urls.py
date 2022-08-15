from django.urls import path

from . import views

app_name = "entries"

urlpatterns = [
    path("report_data/", views.ReportDataView.as_view(), name="report_data"),
    path("list/", views.EntriesListView.as_view(), name="entries_list"),
]
