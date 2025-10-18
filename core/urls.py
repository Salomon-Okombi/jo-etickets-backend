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
# 📘 Configuration Swagger / ReDoc
# ===============================
schema_view = get_schema_view(
    openapi.Info(
        title="JO eTicket API",
        default_version="v1",
        description="API pour la gestion des utilisateurs, offres, billets, paniers et paiements.",
        terms_of_service="https://www.jo-eticket.com/terms/",
        contact=openapi.Contact(email="support@jo-eticket.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

# ===============================
# 🌍 Page d’accueil API
# ===============================
def api_root(request):
    """
    Page d'accueil de l'API principale.
    Affiche un message de bienvenue et les liens vers la documentation.
    """
    return JsonResponse({
        "message": "🎟️ Bienvenue sur l’API JO eTicket !",
        "version": "v1",
        "documentation": {
            "swagger_ui": request.build_absolute_uri("/swagger/"),
            "redoc_ui": request.build_absolute_uri("/redoc/"),
            "schema_json": request.build_absolute_uri("/swagger.json"),
        },
        "apps": {
            "utilisateurs": "/api/utilisateurs/",
            "evenements": "/api/evenements/",
            "offres": "/api/offres/",
            "paniers": "/api/paniers/",
            "commandes": "/api/commandes/",
            "billets": "/api/billets/",
            "statistiques": "/api/statistiques/",
        }
    })

# ===============================
# 🔗 Routes principales
# ===============================
urlpatterns = [
    # Page d’accueil API
    path("", api_root, name="api-root"),

    # Admin Django
    path("admin/", admin.site.urls),

    # Applications API
    path("api/utilisateurs/", include("users.urls")),
    path("api/evenements/", include("evenements.urls")),
    path("api/offres/", include("offres.urls")),
    path("api/paniers/", include("paniers.urls")),
    path("api/commandes/", include("paiements.urls")),
    path("api/billets/", include("billets.urls")),
    path("api/statistiques/", include("analytics.urls")),

    # Documentation interactive
    re_path(r"^swagger(?P<format>\.json|\.yaml)$", schema_view.without_ui(cache_timeout=0), name="schema-json"),
    path("swagger/", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
]

# ===============================
# 🖼️ Fichiers statiques et médias (dev uniquement)
# ===============================
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
