from django.urls import path

from reports import views_api
from django.contrib.auth.decorators import login_required

app_name = "reports"

urlpatterns = [
    path("api/report_data/", login_required(views_api.ReportDataView.as_view()), name="report_data"),
    path("api/report_details/", login_required(views_api.ReportDetailsView.as_view()), name="report_details"),
    path("api/report_entries/", login_required(views_api.ReportEntriesView.as_view()), name="report_entries"),
]
