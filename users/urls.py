from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import UtilisateurRegisterView, UtilisateurDetailView

urlpatterns = [
    path("register/", UtilisateurRegisterView.as_view(), name="utilisateur-register"),
    path("me/", UtilisateurDetailView.as_view(), name="utilisateur-me"),
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
