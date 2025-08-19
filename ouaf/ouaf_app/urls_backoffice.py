from django.urls import path
from . import views_backoffice as v

app_name = "backoffice"

urlpatterns = [
    path("", v.BackofficeHome.as_view(), name="home"),

    path("users/", v.UserListView.as_view(), name="user_list"),
    path("users/<int:pk>/edit/", v.UserUpdateView.as_view(), name="user_edit"),

    path("events/", v.EventListView.as_view(), name="event_list"),
    path("events/new/", v.EventCreateView.as_view(), name="event_create"),
    path("events/<int:pk>/edit/", v.EventUpdateView.as_view(), name="event_edit"),
    path("events/<int:pk>/delete/", v.EventDeleteView.as_view(), name="event_delete"),

    path("animals/", v.AnimalListView.as_view(), name="animal_list"),
]