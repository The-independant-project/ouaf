from django.urls import path, include
from . import views

urlpatterns = [
    path("", views.index, name='index'),
    path('account/logout', views.my_logout, name="my_logout"),
    path("account/", include("django.contrib.auth.urls")),
    path("registration/signup",views.signup_user, name="signup"),
    path("account/edit", views.account_edit, name="account_edit"),
    path("organisationChart", views.organisation_chart, name="organisation_chart"),
    #account/login/ [name='login']
    #account/logout/ [name='logout']
    #account/password_change/ [name='password_change']
    #account/password_change/done/ [name='password_change_done']
    #account/password_reset/ [name='password_reset']
    #account/password_reset/done/ [name='password_reset_done']
    #account/reset/<uidb64>/<token>/ [name='password_reset_confirm']
    #account/reset/done/ [name='password_reset_complete']
]


