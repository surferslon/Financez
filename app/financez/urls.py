from accounts import views as acc_views
from currencies import views as curr_views
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.urls import include, path
from reports import views_templates as report_views
from settings import views as settings_views

urlpatterns = [
    path("", login_required(report_views.MainView.as_view()), name="main"),
    path("i18n/", include("django.conf.urls.i18n")),
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    path("reg/", include("registration.urls")),
    path("change_field", login_required(settings_views.change_field), name="change_field"),
    path("newacc/", login_required(acc_views.NewAccView.as_view()), name="new_acc"),
    path("newcur/", login_required(curr_views.NewCurView.as_view()), name="new_cur"),
    path("changecur/", login_required(settings_views.change_currency), name="change_cur"),
    path("settings/<str:section>", login_required(settings_views.SettingsView.as_view()), name="settings"),
    path("delacc/<int:pk>", login_required(acc_views.DelAccView.as_view()), name="del_acc"),
    path("reports/", include("reports.urls")),
    path("users/", include("users.urls")),
    path("accounts/", include("accounts.urls")),
    path("entries/", include("entries.urls")),
    path("currencies/", include("currencies.urls")),
]
