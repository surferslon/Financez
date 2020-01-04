from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.MainView.as_view(), name='main_book'),
    path('reports/', views.ReportsView.as_view(), name='reports'),
    path('report_data/', views.report_data, name='report_data'),
    path('settings/<str:section>', views.SettingsView.as_view(), name='settings'),
    path('change_field', views.change_field, name='change_field'),
    path('admin/', admin.site.urls),
]
