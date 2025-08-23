from django.urls import path, include
from . import views

app_name = "backoffice"

urlpatterns = [
    path("", views.BackofficeHome.as_view(), name="home"),

    path("users/", views.UserListView.as_view(), name="user_list"),
    path("users/<int:pk>/edit/", views.UserUpdateView.as_view(), name="user_edit"),

    path("services/", views.ServiceListView.as_view(), name="service_list"),
    path("services/<int:pk>/update/", views.ServiceUpdateView.as_view(), name="service_update"),

    path("events/", views.EventListView.as_view(), name="event_list"),
    path("events/new/", views.EventCreateView.as_view(), name="event_create"),
    path("events/<int:pk>/edit/", views.EventUpdateView.as_view(), name="event_edit"),
    path("events/<int:pk>/delete/", views.EventDeleteView.as_view(), name="event_delete"),

    path("animals/", views.AnimalListView.as_view(), name="animal_list"),
]