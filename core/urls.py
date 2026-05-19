from django.contrib import admin
from django.urls import path, include, re_path
from django.http import JsonResponse
from django.conf import settings
from django.conf.urls.static import static

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


# ===============================
# Swagger / ReDoc
# ===============================

schema_view = get_schema_view(
    openapi.Info(
        title="JO eTicket API",
        default_version="v1",
        description="API JO eTicket",
        contact=openapi.Contact(email="support@jo-eticket.com"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

# ===============================
# API ROOT
# ===============================

def api_root(request):
    return JsonResponse({
        "message": "API JO eTicket",
        "version": "v1",
    })


# ===============================
# URLS PRINCIPALES
# ===============================

urlpatterns = [
    path("", api_root, name="api-root"),
    path("admin/", admin.site.urls),

    # API
    path("api/utilisateurs/", include("users.urls")),
    path("api/evenements/", include("evenements.urls")),
    path("api/offres/", include("offres.urls")),
    path("api/paniers/", include("paniers.urls")),
    path("api/commandes/", include("commandes.urls")),
    path("api/billets/", include("billets.urls")),
]

# ===============================
# APPS OPTIONNELLES
# ===============================

if "paiements.apps.PaiementsConfig" in settings.INSTALLED_APPS:
    urlpatterns += [
        path("api/paiements/", include("paiements.urls")),
    ]

if "analytics.apps.AnalyticsConfig" in settings.INSTALLED_APPS:
    urlpatterns += [
        path("api/statistiques/", include("analytics.urls")),
        path("api/stats/", include("analytics.overview_urls")),
    ]

# ===============================
# DOCS
# ===============================

urlpatterns += [
    re_path(
        r"^swagger(?P<format>\.json|\.yaml)$",
        schema_view.without_ui(cache_timeout=0),
    ),
    path("swagger/", schema_view.with_ui("swagger", cache_timeout=0)),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0)),
]

# ===============================
#  MEDIA FILES (IMPORTANT IMAGE FIX)
# ===============================

#  DEV ONLY
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# PROD (Render) → obligatoire pour afficher les images
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)