# core/urls.py
from django.contrib import admin
from django.urls import path, include, re_path
from django.http import JsonResponse
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# ===============================
#  Swagger / ReDoc
# ===============================
schema_view = get_schema_view(
    openapi.Info(
        title="JO eTicket API",
        default_version="v1",
        description="API pour la gestion des utilisateurs, offres, billets, paniers et paiements.",
        contact=openapi.Contact(email="support@jo-eticket.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

# ===============================
#  API root
# ===============================
def api_root(request):
    return JsonResponse({
        "message": " Bienvenue sur l’API JO eTicket",
        "version": "v1",
        "apps": {
            "utilisateurs": "/api/utilisateurs/",
            "evenements": "/api/evenements/",
            "offres": "/api/offres/",
            "paniers": "/api/paniers/",
            "commandes": "/api/commandes/",
            "billets": "/api/billets/",
            "paiements": "/api/paiements/",
            "statistiques": "/api/statistiques/",
        },
        "docs": {
            "swagger": "/swagger/",
            "redoc": "/redoc/",
        },
    })

# ===============================
#  URL patterns
# ===============================
urlpatterns = [
    path("", api_root, name="api-root"),
    path("admin/", admin.site.urls),

    # Apps toujours présentes
    path("api/utilisateurs/", include("users.urls")),
    path("api/evenements/", include("evenements.urls")),
    path("api/offres/", include("offres.urls")),
    path("api/paniers/", include("paniers.urls")),
    path("api/commandes/", include("commandes.urls")),
    path("api/billets/", include("billets.urls")),
]

# ===============================
#  Apps métier conditionnelles
# (évite erreurs app_label en prod)
# ===============================
if "paiements.apps.PaiementsConfig" in settings.INSTALLED_APPS:
    urlpatterns += [
        path("api/paiements/", include("paiements.urls")),
    ]

if "analytics.apps.AnalyticsConfig" in settings.INSTALLED_APPS:
    urlpatterns += [
        path("api/statistiques/", include("analytics.urls")),
    ]

# ===============================
#  Documentation
# ===============================
urlpatterns += [
    re_path(
        r"^swagger(?P<format>\.json|\.yaml)$",
        schema_view.without_ui(cache_timeout=0),
        name="schema-json",
    ),
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path(
        "redoc/",
        schema_view.with_ui("redoc", cache_timeout=0),
        name="schema-redoc",
    ),
]

# ===============================
#  Static / media (dev only)
# ===============================
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)