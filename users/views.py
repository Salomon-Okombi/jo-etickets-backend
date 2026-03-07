from rest_framework import generics, permissions, filters
from rest_framework.permissions import IsAdminUser
from .models import Utilisateur
from .serializers import UtilisateurSerializer, UtilisateurRegisterSerializer

# =========================
# PUBLIC / AUTH
# =========================

class UtilisateurRegisterView(generics.CreateAPIView):
    queryset = Utilisateur.objects.all()
    serializer_class = UtilisateurRegisterSerializer
    permission_classes = [permissions.AllowAny]


class UtilisateurDetailView(generics.RetrieveUpdateAPIView):
    """
    Profil utilisateur connecté :
    - GET  /api/utilisateurs/me/
    - PATCH/PUT /api/utilisateurs/me/
    """
    serializer_class = UtilisateurSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


# =========================
# ADMIN (LIST / CRUD USERS)
# =========================

class AdminUtilisateurListView(generics.ListAPIView):
    """
    Liste paginée des utilisateurs (ADMIN ONLY)
    - GET /api/utilisateurs/?search=...&ordering=...
    """
    queryset = Utilisateur.objects.all().order_by("-date_creation")
    serializer_class = UtilisateurSerializer
    permission_classes = [IsAdminUser]

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["username", "email", "type_compte", "statut"]
    ordering_fields = ["id", "username", "email", "type_compte", "statut", "date_creation"]
    ordering = ["-date_creation"]


class AdminUtilisateurDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Détail / Update / Delete utilisateur (ADMIN ONLY)
    - GET    /api/utilisateurs/<id>/
    - PATCH  /api/utilisateurs/<id>/
    - DELETE /api/utilisateurs/<id>/
    """
    queryset = Utilisateur.objects.all()
    serializer_class = UtilisateurSerializer
    permission_classes = [IsAdminUser]