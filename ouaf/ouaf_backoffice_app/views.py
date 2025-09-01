from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import PermissionRequiredMixin
from django import forms
from django.contrib import messages
from django.forms import inlineformset_factory
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, ListView, DeleteView, UpdateView, CreateView, DetailView
from .mixins import BackofficeAccessRequiredMixin
from ouaf_app.models import Event, Animal, Activity, OrganisationChartEntry, ActivityMedia, ActivityCategory
from .forms import PersonEditForm
from ouaf_app.signals import *
from django.db import transaction

User = get_user_model()


#On top of the page for better compatibility
def _is_ajax(request):
    return request.headers.get("x-requested-with") == "XMLHttpRequest"


class BackofficeHome(BackofficeAccessRequiredMixin, TemplateView):
    template_name = "backoffice/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["sections"] = [
            {"label": "Utilisateurs", "url": reverse_lazy("backoffice:user_list")},
            {"label": "Événements", "url": reverse_lazy("backoffice:event_list")},
            {"label": "Animaux", "url": reverse_lazy("backoffice:animal_list")},
            {"label": "Activites", "url": reverse_lazy("backoffice:activity_list")},
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
class AnimalCreateView(BackofficeAccessRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Animal
    fields = ["name", "description", "birth", "death", "pet_amount"]
    template_name = "backoffice/animals/form.html"
    permission_required = animal_add.perm_name()
    success_url = reverse_lazy('backoffice:animal_list')
    raise_exception = True
class AnimalEditView(BackofficeAccessRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Animal
    fields = ["name", "description", "birth", "death", "pet_amount"]
    template_name = "backoffice/animals/update.html"
    permission_required = animal_change.perm_name()
    success_url = reverse_lazy('backoffice:animal_list')
    raise_exception = True
class AnimalDeleteView(BackofficeAccessRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Animal
    template_name = "backoffice/animals/confirm_delete.html"
    permission_required = animal_delete.perm_name()
    success_url = reverse_lazy('backoffice:animal_list')
    raise_exception = True

class ActivityListView(BackofficeAccessRequiredMixin, PermissionRequiredMixin, ListView):
    model = Activity
    template_name = "backoffice/activities/list.html"
    permission_required = activity_view.perm_name()
    raise_exception = True

    def get_queryset(self):
        return (
            Activity.objects
            .all()
            .prefetch_related("media")
        )


class ActivityCreateView(BackofficeAccessRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Activity
    fields = ["title", "category", "description"]
    template_name = "backoffice/activities/form.html"
    permission_required = activity_add.perm_name()
    success_url = reverse_lazy("backoffice:activity_list")
    raise_exception = True

    def _create_formset_class(self):
        return inlineformset_factory(
            Activity,
            ActivityMedia,
            fields=["file", "url", "caption", "position"],
            extra=2,
            can_delete=True,
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        FormSet = self._create_formset_class()
        if self.request.method == "POST":
            ctx["media_formset"] = FormSet(self.request.POST, self.request.FILES)
        else:
            ctx["media_formset"] = FormSet()
        return ctx

    def post(self, request, *args, **kwargs):
        self.object = None
        form = self.get_form()
        FormSet = self._create_formset_class()
        media_formset = FormSet(request.POST, request.FILES)

        if form.is_valid() and media_formset.is_valid():
            with transaction.atomic():
                self.object = form.save()
                media_formset.instance = self.object
                media_formset.save()

            messages.success(request, "Activité créée.")
            return redirect(self.get_success_url())

        context = self.get_context_data(form=form)
        return self.render_to_response(context)


class ActivityCategoryCreateModalView(BackofficeAccessRequiredMixin, PermissionRequiredMixin, CreateView):
    model = ActivityCategory
    fields = ["title", "image"]
    template_name = "backoffice/activities/partials/category_form.html"
    permission_required = activity_add.perm_name()
    raise_exception = True

    def form_valid(self, form):
        obj = form.save()
        if _is_ajax(self.request):
            return JsonResponse({"id": obj.id, "title": obj.title})
        return super().form_valid(form)

    def form_invalid(self, form):
        if _is_ajax(self.request):
            return self.render_to_response(self.get_context_data(form=form), status=400)
        return super().form_invalid(form)


class ActivityCategoryCreateView(BackofficeAccessRequiredMixin, PermissionRequiredMixin, CreateView):
    model = ActivityCategory
    fields = ["title", "image"]
    template_name = "backoffice/activities/category_form.html"
    permission_required = activity_add.perm_name()
    raise_exception = True

    def get_success_url(self):
        nxt = self.request.GET.get("next") or self.request.POST.get("next")
        return nxt or reverse_lazy("backoffice:activity_create")


class ActivityDetailView(BackofficeAccessRequiredMixin, PermissionRequiredMixin, DetailView):
    model = Activity
    template_name = "backoffice/activities/detail.html"
    permission_required = activity_view.perm_name()
    raise_exception = True

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["media_list"] = self.object.media.all().order_by("position", "id")
        return ctx


class ActivityUpdateView(BackofficeAccessRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Activity
    fields = ["title", "category", "description"]
    template_name = "backoffice/activities/update.html"
    permission_required = activity_change.perm_name()
    success_url = reverse_lazy("backoffice:activity_list")
    raise_exception = True

    def _update_formset_class(self):
        return inlineformset_factory(
            Activity,
            ActivityMedia,
            fields=["file", "url", "caption", "position"],
            extra=0,
            can_delete=True
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        UpdateFormSet = self._update_formset_class()
        if self.request.method == "POST":
            ctx["media_formset"] = UpdateFormSet(self.request.POST, self.request.FILES, instance=self.object)
        else:
            ctx["media_formset"] = UpdateFormSet(instance=self.object)
        return ctx

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        UpdateFormSet = self._update_formset_class()
        media_formset = UpdateFormSet(request.POST, request.FILES, instance=self.object)

        if form.is_valid() and media_formset.is_valid():
            with transaction.atomic():
                self.object = form.save()
                media_formset.save()
            messages.success(request, "Activité mise à jour.")
            return redirect(self.get_success_url())

        return self.render_to_response({
            "form": form,
            "object": self.object,
            "media_formset": media_formset,
        })


class ActivityDeleteView(BackofficeAccessRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Activity
    template_name = "backoffice/activities/confirm_delete.html"
    permission_required = activity_delete.perm_name()
    success_url = reverse_lazy("backoffice:activity_list")
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
