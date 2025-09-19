from django.db.models import Prefetch
from django.shortcuts import render, redirect
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.decorators import login_required, login_not_required
from django.urls import reverse_lazy
from django.views.generic import ListView, FormView
from django.http import HttpRequest
from .forms import PersonForm, RegistrationForm, ContactForm
from .models import OrganisationChartEntry, Activity, ActivityCategory, Animal, AnimalMedia
from django.contrib import messages
from django.utils.translation import gettext as _


# Create your views here.

def index(request):
    return render(request, "index.html")


def my_logout(request):
    logout(request)
    return redirect("/")


def signup_user(request: HttpRequest):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            new_user = authenticate(username=form.cleaned_data['username'],
                                    password=form.cleaned_data['password1'])
            login(request, new_user)
            return redirect("/")
        else:
            print(form.errors)
    else:
        form = RegistrationForm()
    template_name = "registration/signup.html"
    context = {"form": form}
    return render(request, template_name, context)


@login_required
def account_edit(request):
    if request.method == "POST":
        form = PersonForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
        else:
            print(form.errors)
    else:
        form = PersonForm(instance=request.user)
    template_name = "account/account_edit.html"
    context = {"form": form}
    return render(request, template_name, context)


def organisation_chart(request):
    context = {"organisation_members": OrganisationChartEntry.objects.all()}
    return render(request, "organisationChart.html", context)


def mediation_animale(request):
    return render(request, "mediationAnimale.html")


def confidentialite(request):
    return render(request, "confidentialite.html")


class ActivityCategoryListView(ListView):
    model = ActivityCategory
    template_name = "activities/list.html"
    context_object_name = "categories"
    raise_exception = True

class ActivitiesByCategoryView(ListView):
    model = Activity
    template_name = "activities/by_category.html"
    context_object_name = "activities"

    def get_queryset(self):
        return Activity.objects.filter(category_id=self.kwargs["pk"]).order_by("title")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["category"] = ActivityCategory.objects.get(pk=self.kwargs["pk"])
        return ctx

class ContactView(FormView):
    template_name = "contact/contact.html"
    form_class = ContactForm

    def get_success_url(self):
        return reverse_lazy("contact")

    def form_valid(self, form):
        #!!!!!!!!!!! here mail server !!!!!!!!!!!!!!!!!
        messages.success(self.request, "Merci ! Votre message a bien été enregistré. Nous vous répondrons au plus vite.")
        return super().form_valid(form)


def animal_list(request):
    animals = Animal.objects.prefetch_related(Prefetch("media", to_attr="medias")).all()
    for animal in animals:
        if animal.medias:
            pres_image = next(media for media in animal.medias if media.is_image)
            if pres_image:
                animal.presentation_image = pres_image.file
    return render(request, "animals/list.html", { "animals": animals })
def animal_detail(request, animal_id):
    animal = Animal.objects.filter(id=animal_id).first()
    medias = AnimalMedia.objects.filter(animal_id=animal_id)
    if medias:
        pres_image = next(media for media in medias if media.is_image)
        if pres_image:
            animal.presentation_image = pres_image.file
    return render(request, "animals/detail.html", { "animal": animal, "medias": medias })