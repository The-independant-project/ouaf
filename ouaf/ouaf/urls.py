"""
URL configuration for ouaf project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from django.views.i18n import JavaScriptCatalog
from django.conf.urls.i18n import i18n_patterns



urlpatterns = [
    #path("admin/", admin.site.urls), no need to use that because we include it in the urlspatterns
    path("", include('ouaf_app.urls')),
    path("index/", RedirectView.as_view(url="/", permanent=True)),
    path("i18n/", include("django.conf.urls.i18n")),
    # TO use i18n within JS scripts #
    path("jsi18n/", JavaScriptCatalog.as_view(), name="javascript-catalog"),
]

urlpatterns += i18n_patterns(
    path("admin/", admin.site.urls),
    path("", include("ouaf_app.urls")),
    path("backoffice/", include('ouaf_backoffice_app.urls')),
    prefix_default_language=True,
)

if settings.DEBUG:
    from debug_toolbar.toolbar import debug_toolbar_urls
    # Dev
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + debug_toolbar_urls()
else:
    # Prod sans Nginx/Apache
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    ]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)