from accounts import views as acc_views
from currencies import views as curr_views
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.urls import include, path
from entries import views as entries_views
from reports import views as reports_views
from settings import views as settings_views

urlpatterns = [
    path("i18n/", include("django.conf.urls.i18n")),
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    path("reg/", include("registration.urls")),
    path("", login_required(reports_views.MainView.as_view()), name="main"),
    path("entries/", login_required(entries_views.EntriesView.as_view()), name="entries"),
    path("report_data/", login_required(reports_views.ReportDataView.as_view()), name="report_data"),
    path("report_details/", login_required(reports_views.ReportDetailsView.as_view()), name="report_details"),
    path("report_entries/", login_required(reports_views.ReportEntriesView.as_view()), name="report_entries"),
    path("settings/<str:section>", login_required(settings_views.SettingsView.as_view()), name="settings"),
    path("change_field", login_required(reports_views.change_field), name="change_field"),
    path("newacc/", login_required(acc_views.NewAccView.as_view()), name="new_acc"),
    path("newcur/", login_required(curr_views.NewCurView.as_view()), name="new_cur"),
    path("changecur/", login_required(settings_views.change_currency), name="change_cur"),
    path("delacc/<int:pk>", login_required(acc_views.DelAccView.as_view()), name="del_acc"),
    path("api/report_data/", reports_views.ReportDataView.as_view()),
    path("api/users/", include("users.urls")),
    path("api/accounts/", include("accounts.urls")),
    path("api/entries/", include("entries.urls")),
    path("api/currencies/", include("currencies.urls")),
]
