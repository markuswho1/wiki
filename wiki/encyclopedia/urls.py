from django.urls import path

from .views import show_entry, index, search, newEntry, edit_page, show_error

app_name = "wiki"

urlpatterns = [
    path("", index, name="index"),
    path("search/", search, name="search"),
    path("<str:title>", show_entry, name="entries"),
    path("new/", newEntry, name="new"),
    path("edit/<str:entry>", edit_page, name="edit"),
    path("error/<str:error_message>", show_error, name="error"),
]