from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Utilisateur, HistoriqueConnexion


@admin.register(Utilisateur)
class UtilisateurAdminDebug(UserAdmin):
    """
    ADMIN TEMPORAIRE DE DEBUG
     À SUPPRIMER APRÈS CORRECTION DU ROOT
    """

    list_display = (
        "id",
        "username",
        "email",
        "role",
        "is_staff",
        "is_superuser",
        "is_active",
    )

    list_filter = (
        "role",
        "is_staff",
        "is_superuser",
        "is_active",
    )

    search_fields = ("username", "email")

    ordering = ("-id",)

    # On affiche TOUTES LES CHOSES UTILES
    fieldsets = (
        (None, {
            "fields": (
                "username",
                "password",
            )
        }),
        ("Informations personnelles", {
            "fields": (
                "email",
                "first_name",
                "last_name",
                "telephone",
                "photo_profil",
            )
        }),
        ("Droits", {
            "fields": (
                "role",
                "is_active",
                "is_staff",
                "is_superuser",
                "groups",
                "user_permissions",
            )
        }),
        ("Sécurité / état", {
            "fields": (
                "est_verifie",
                "est_bloque",
                "tentatives_connexion",
                "derniere_connexion_ip",
                "last_login",
                "date_joined",
            )
        }),
    )

    readonly_fields = (
        "last_login",
        "date_joined",
    )


@admin.register(HistoriqueConnexion)
class HistoriqueConnexionAdmin(admin.ModelAdmin):
    list_display = (
        "utilisateur",
        "date_connexion",
        "statut_connexion",
        "type_action",
    )