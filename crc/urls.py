from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.urls import include, path

# Language switcher endpoint (not language-prefixed).
urlpatterns = [
    path("i18n/", include("django.conf.urls.i18n")),
]

# All app and admin URLs are served under a language prefix:
# /en/..., /az/..., /ru/..., /tr/... (default language is prefixed too).
urlpatterns += i18n_patterns(
    path("admin/", admin.site.urls),
    path("", include("app.urls")),
    prefix_default_language=True,
)