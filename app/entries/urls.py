from django.urls import path

from . import views

app_name = "entries"

urlpatterns = [
    path("report_data/", views.ReportDataView.as_view(), name="report_data"),
    path("report_details/<int:acc_id>", views.ReportDetailsView.as_view(), name="report_details"),
    path("report_entries/<int:acc_id>", views.AccEntriesView.as_view(), name="report_entries"),
    path("list/", views.EntriesListView.as_view(), name="entries_list"),
    path("create/", views.EntryCreateView.as_view(), name="entries_create"),
]
