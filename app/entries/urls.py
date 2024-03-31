from django.contrib.auth.decorators import login_required
from django.urls import path
from entries import views_api, views_templates

app_name = "entries"

urlpatterns = [
    path("index/", login_required(views_templates.EntriesView.as_view()), name="index"),
    path("api/list/", login_required(views_api.EntriesListView.as_view()), name="list"),
    path("api/create/", login_required(views_api.EntryCreateView.as_view()), name="create"),
    path("api/read/<int:pk>/", login_required(views_api.ModalReadEntryView.as_view()), name="read"),
    path("api/update/<int:pk>/", login_required(views_api.EntryUpdateView.as_view()), name="update"),
]
