#users/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Utilisateur, HistoriqueConnexion


@admin.register(Utilisateur)
class UtilisateurAdmin(UserAdmin):

    # colonnes affichées dans la liste
    list_display = (
        "username",
        "email",
        "role",
        "est_verifie",
        "is_active",
        "date_joined",
        "last_login",
        "tentatives_connexion",
    )

    list_filter = (
        "role",
        "est_verifie",
        "is_staff",
        "is_superuser",
        "is_active",
    )

    search_fields = (
        "username",
        "email",
    )

    ordering = ("-date_joined",)

    fieldsets = UserAdmin.fieldsets + (
        ("Informations supplémentaires", {
            "fields": (
                "role",
                "telephone",
                "photo_profil",
                "est_verifie",
                "est_bloque",
                "tentatives_connexion",
                "derniere_connexion_ip",
            )
        }),
    )

    readonly_fields = (
        "date_joined",
        "last_login",
    )


@admin.register(HistoriqueConnexion)
class HistoriqueConnexionAdmin(admin.ModelAdmin):

    list_display = (
        "utilisateur",
        "date_connexion",
        "adresse_ip",
        "statut_connexion",
        "type_action",
    )

    list_filter = (
        "statut_connexion",
        "type_action",
        "date_connexion",
    )

    search_fields = (
        "utilisateur__username",
        "utilisateur__email",
        "adresse_ip",
    )

    ordering = ("-date_connexion",)

    readonly_fields = (
        "date_connexion",
    )