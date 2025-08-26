from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import TemplateView, ListView, DeleteView, UpdateView, CreateView
from .mixins import BackofficeAccessRequiredMixin
from ouaf_app.models import Event, Animal, Activite, OrganisationChartEntry
from .forms import PersonEditForm
from ouaf_app.signals import *

User = get_user_model()


class BackofficeHome(BackofficeAccessRequiredMixin, TemplateView):
    template_name = "backoffice/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["sections"] = [
            {"label": "Utilisateurs", "url": reverse_lazy("backoffice:user_list")},
            {"label": "Événements", "url": reverse_lazy("backoffice:event_list")},
            {"label": "Animaux", "url": reverse_lazy("backoffice:animal_list")},
            {"label": "Activites", "url": reverse_lazy("backoffice:activite_list")},
            {"label": "Team Members", "url": reverse_lazy("backoffice:team_list")}
            ##
        ]
        return context


class UserListView(BackofficeAccessRequiredMixin, PermissionRequiredMixin, ListView):
    model = User
    template_name = "backoffice/users/list.html"
    permission_required = person_view.perm_name()
    raise_exception = True


class UserUpdateView(BackofficeAccessRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = User
    form_class = PersonEditForm
    template_name = 'backoffice/users/form.html'
    permission_required = person_change.perm_name()
    success_url = reverse_lazy("backoffice:user_list")
    raise_exception = True


class EventListView(BackofficeAccessRequiredMixin, PermissionRequiredMixin, ListView):
    model = Event
    template_name = "backoffice/events/list.html"
    permission_required = event_view.perm_name()
    raise_exception = True


class EventCreateView(BackofficeAccessRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Event
    fields = ["summary", "description", "start", "until", "duration",
              "organizer", "attendees", "address", "latitude", "longitude", "is_published"]
    template_name = "backoffice/events/form.html"
    permission_required = event_add.perm_name()
    success_url = reverse_lazy("backoffice:event_list")
    raise_exception = True


class EventUpdateView(BackofficeAccessRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Event
    fields = ["summary", "description", "start", "until", "duration",
              "organizer", "attendees", "address", "latitude", "longitude", "is_published"]
    template_name = "backoffice/events/form.html"
    permission_required = event_change.perm_name()
    success_url = reverse_lazy("backoffice:event_list")
    raise_exception = True


class EventDeleteView(BackofficeAccessRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Event
    template_name = "backoffice/events/confirm_delete.html"
    permission_required = event_delete.perm_name()
    success_url = reverse_lazy('backoffice:event_list')
    raise_exception = True


class AnimalListView(BackofficeAccessRequiredMixin, PermissionRequiredMixin, ListView):
    model = Animal
    template_name = "backoffice/animals/list.html"
    permission_required = animal_view.perm_name()
    raise_exception = True


class ActiviteListView(BackofficeAccessRequiredMixin, PermissionRequiredMixin, ListView):
    model = Activite
    template_name = "backoffice/activites/list.html"
    permission_required = activite_view.perm_name()
    raise_exception = True


class ActiviteCreateView(BackofficeAccessRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Activite
    fields = ["title", "description", "image"]
    template_name = "backoffice/activites/form.html"
    permission_required = activite_add.perm_name()
    success_url = reverse_lazy("backoffice:activite_list")
    raise_exception = True


class ActiviteUpdateView(BackofficeAccessRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Activite
    fields = ["title", "description", "image"]
    template_name = "backoffice/activites/update.html"
    permission_required = activite_change.perm_name()
    success_url = reverse_lazy("backoffice:activite_list")
    raise_exception = True


class ActiviteDeleteView(BackofficeAccessRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Activite
    template_name = "backoffice/activites/confirm_delete.html"
    permission_required = activite_delete.perm_name()
    success_url = reverse_lazy('backoffice:activite_list')
    raise_exception = True


class TeamMemberListView(BackofficeAccessRequiredMixin, PermissionRequiredMixin, ListView):
    model = OrganisationChartEntry
    template_name = "backoffice/team/list.html"
    permission_required = organisationChartEntry_view.perm_name()
    raise_exception = True


class TeamMemberCreateView(BackofficeAccessRequiredMixin, PermissionRequiredMixin, CreateView):
    model = OrganisationChartEntry
    fields = ["first_name", "last_name", "role", "description", "photo"]
    template_name = "backoffice/team/form.html"
    permission_required = organisationChartEntry_add.perm_name()
    success_url = reverse_lazy("backoffice:team_list")
    raise_exception = True


class TeamMemberUpdateView(BackofficeAccessRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = OrganisationChartEntry
    fields = ["first_name", "last_name", "role", "description", "photo"]
    template_name = "backoffice/team/update.html"
    permission_required = organisationChartEntry_change.perm_name()
    success_url = reverse_lazy("backoffice:team_list")
    raise_exception = True


class TeamMemberDeleteView(BackofficeAccessRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = OrganisationChartEntry
    template_name = "backoffice/team/confirm_delete.html"
    permission_required = organisationChartEntry_delete.perm_name()
    success_url = reverse_lazy("backoffice:team_list")
    raise_exception = True
