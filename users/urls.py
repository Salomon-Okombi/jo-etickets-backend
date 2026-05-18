# users/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import (
    UtilisateurRegisterView,
    UtilisateurDetailView,
    AdminUtilisateurViewSet,
)

# =========================
# ROUTES ADMIN (séparées)
# /api/users/admin/
# =========================

admin_router = DefaultRouter()
admin_router.register(
    r"users",
    AdminUtilisateurViewSet,
    basename="admin-utilisateurs"
)

# =========================
# ROUTES UTILISATEUR (PUBLIC / CONNECTÉ)
# =========================

urlpatterns = [
    # Auth / utilisateur connecté
    path("register/", UtilisateurRegisterView.as_view(), name="utilisateur-register"),
    path("me/", UtilisateurDetailView.as_view(), name="utilisateur-me"),

    # JWT
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    # Admin (isolé)
    path("admin/", include(admin_router.urls)),
]