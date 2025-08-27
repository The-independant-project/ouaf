from django.urls import path, include
from . import views

app_name = "backoffice"

urlpatterns = [
    path("", views.BackofficeHome.as_view(), name="home"),

    path("users/", views.UserListView.as_view(), name="user_list"),
    path("users/<int:pk>/edit/", views.UserUpdateView.as_view(), name="user_edit"),

    path("activities/", views.ActivityListView.as_view(), name="activity_list"),
    path("activities/new/", views.ActivityCreateView.as_view(), name="activity_create"),
    path("activities/<int:pk>/", views.ActivityDetailView.as_view(), name="activity_detail"),
    path("activities/<int:pk>/update/", views.ActivityUpdateView.as_view(), name="activity_update"),
    path("activities/<int:pk>/delete/", views.ActivityDeleteView.as_view(), name="activity_delete"),
    path("activities/categories/new/modal/",views.ActivityCategoryCreateModalView.as_view(),
         name="activity_category_modal",),

    path("events/", views.EventListView.as_view(), name="event_list"),
    path("events/new/", views.EventCreateView.as_view(), name="event_create"),
    path("events/<int:pk>/edit/", views.EventUpdateView.as_view(), name="event_edit"),
    path("events/<int:pk>/delete/", views.EventDeleteView.as_view(), name="event_delete"),

    path("animals/", views.AnimalListView.as_view(), name="animal_list"),

    path("team/", views.TeamMemberListView.as_view(), name="team_list"),
    path("team/new", views.TeamMemberCreateView.as_view(), name="team_create"),
    path("team/<int:pk>/edit/", views.TeamMemberUpdateView.as_view(), name="team_update"),
    path("team/<int:pk>/delete/", views.TeamMemberDeleteView.as_view(), name="team_delete")
]