from rest_framework import permissions


class IsOwnerOrStaff(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user and request.user.is_authenticated and request.user.is_staff:
            return True
        return obj.utilisateur_id == getattr(request.user, "id", None)