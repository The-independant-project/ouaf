from django.shortcuts import render, redirect
from django.contrib.auth import logout, authenticate, login
from .forms import PersonForm



# Create your views here.

def index(request):
    return render(request, "index.html")

def my_logout(request):
    logout(request)
    return redirect("/")


def signup_user(request):
    if request.method == "POST":
        form = PersonForm(request.POST)
        if form.is_valid():
            form.save()
            new_user = authenticate(username=form.cleaned_data['username'],
                                    password=form.cleaned_data['password1'])
            login(request, new_user)
            return redirect("/")
        else:
            print(form.errors)
    else:
        form = PersonForm()
    template_name = "registration/signup.html"
    context = { "form":form }
    return render(request, template_name, context)