from rest_framework import generics, permissions, viewsets, filters
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from .models import Utilisateur
from .serializers import (
    UtilisateurSerializer,
    UtilisateurRegisterSerializer,
    AdminUserCreateSerializer,
    AdminUserUpdateSerializer,
)

# =========================
# PUBLIC / AUTH
# =========================

class UtilisateurRegisterView(generics.CreateAPIView):
    queryset = Utilisateur.objects.all()
    serializer_class = UtilisateurRegisterSerializer
    permission_classes = [permissions.AllowAny]


class UtilisateurDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = UtilisateurSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


# =========================
# ✅ ADMIN CRUD USERS
# =========================

class AdminUtilisateurViewSet(viewsets.ModelViewSet):
    """
    CRUD Admin sur les utilisateurs
    Base URL (via core/urls.py): /api/utilisateurs/
    - GET    /api/utilisateurs/
    - POST   /api/utilisateurs/
    - GET    /api/utilisateurs/<id>/
    - PATCH  /api/utilisateurs/<id>/
    - DELETE /api/utilisateurs/<id>/
    """
    queryset = Utilisateur.objects.all().order_by("-date_creation")
    permission_classes = [IsAdminUser]

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["username", "email", "type_compte", "statut"]
    ordering_fields = ["id", "username", "email", "type_compte", "statut", "date_creation"]
    ordering = ["-date_creation"]

    def get_serializer_class(self):
        if self.action == "create":
            return AdminUserCreateSerializer
        if self.action in ["update", "partial_update"]:
            return AdminUserUpdateSerializer
        return UtilisateurSerializer

    def destroy(self, request, *args, **kwargs):
        user = self.get_object()

        # Sécurité simple: empêcher suppression de soi-même
        if user.id == request.user.id:
            return Response({"detail": "Impossible de supprimer votre propre compte."}, status=400)

        # (optionnel) empêcher suppression superuser
        if getattr(user, "is_superuser", False):
            return Response({"detail": "Impossible de supprimer un super-admin."}, status=400)

        return super().destroy(request, *args, **kwargs)