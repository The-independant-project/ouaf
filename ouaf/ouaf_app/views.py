from django.shortcuts import render, redirect
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.decorators import login_required, login_not_required
from django.views.generic import ListView
from django.http import HttpRequest
from .forms import PersonForm, RegistrationForm
from .models import OrganisationChartEntry, Activite


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


class ActiviteListView(ListView):
    model = Activite
    template_name = "activites/list.html"
    raise_exception = True
