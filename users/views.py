#users : views.py
from rest_framework import generics, permissions, viewsets, filters
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser

from .models import Utilisateur
from .serializers import (
    UtilisateurProfileSerializer,
    UtilisateurRegisterSerializer,
    UtilisateurAdminReadSerializer,
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
    """
    GET /api/utilisateurs/me/
    PATCH /api/utilisateurs/me/
    """
    serializer_class = UtilisateurProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_object(self):
        return self.request.user


# =========================
# ADMIN CRUD UTILISATEURS
# =========================

class AdminUtilisateurViewSet(viewsets.ModelViewSet):
    queryset = Utilisateur.objects.all().order_by("-date_creation")
    permission_classes = [IsAdminUser]

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = [
        "username",
        "email",
        "first_name",
        "last_name",
        "telephone",
    ]
    ordering_fields = [
        "id",
        "username",
        "email",
        "date_creation",
    ]
    ordering = ["-date_creation"]

    def get_serializer_class(self):
        if self.action == "create":
            return AdminUserCreateSerializer
        if self.action in ["update", "partial_update"]:
            return AdminUserUpdateSerializer
        return UtilisateurAdminReadSerializer

    def destroy(self, request, *args, **kwargs):
        user = self.get_object()

        # empêcher suppression de soi-même
        if user.id == request.user.id:
            return Response(
                {"detail": "Impossible de supprimer votre propre compte."},
                status=400,
            )

        # empêcher suppression d’un super-admin
        if user.is_superuser:
            return Response(
                {"detail": "Impossible de supprimer un super-admin."},
                status=400,
            )

        return super().destroy(request, *args, **kwargs)