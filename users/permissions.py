# users/permissions.py
from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Permission personnalisée :
    - Lecture autorisée pour tous (méthodes SAFE).
    - Écriture/modification uniquement pour le propriétaire de l’objet.
    """

    def has_object_permission(self, request, view, obj):
        # Méthodes de lecture autorisées à tous (GET, HEAD, OPTIONS)
        if request.method in permissions.SAFE_METHODS:
            return True

        # Vérifie si l'objet a un attribut "utilisateur"
        owner = getattr(obj, "utilisateur", None)
        return owner == request.user
