from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import (
    UtilisateurRegisterView,
    UtilisateurDetailView,
    AdminUtilisateurListView,
    AdminUtilisateurDetailView,
)

urlpatterns = [
    # ADMIN USERS (IMPORTANT)
    # Comme core/urls.py a déjà "api/utilisateurs/", ici c'est la racine :
    path("", AdminUtilisateurListView.as_view(), name="admin-utilisateurs-list"),
    path("<int:pk>/", AdminUtilisateurDetailView.as_view(), name="admin-utilisateurs-detail"),

    # AUTH / ACCOUNT
    path("register/", UtilisateurRegisterView.as_view(), name="utilisateur-register"),
    path("me/", UtilisateurDetailView.as_view(), name="utilisateur-me"),

    # JWT
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]