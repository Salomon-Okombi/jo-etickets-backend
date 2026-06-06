# Last edited by you@example.com @ 05/06/26 18:47.
#users/admin
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Utilisateur, HistoriqueConnexion


@admin.register(Utilisateur)
class UtilisateurAdmin(UserAdmin):

    list_display = (
        "username",
        "email",
        "role",
        "is_active",
        "est_verifie",
        "est_bloque",
        "is_staff",
        "date_joined",
    )

    list_filter = (
        "role",
        "is_active",
        "is_staff",
        "est_verifie",
        "est_bloque",
    )

    search_fields = ("username", "email", "telephone")
    ordering = ("-date_joined",)

    fieldsets = (
        ("Identité", {
            "fields": (
                "username",
                "email",
                "first_name",
                "last_name",
                "telephone",
                "photo_profil",
            )
        }),
        ("Sécurité", {
            "fields": (
                "password",
                "last_login",
                "tentatives_connexion",
                "derniere_connexion_ip",
            )
        }),
        ("Statut", {
            "fields": (
                "role",
                "is_active",
                "est_verifie",
                "est_bloque",
            )
        }),
        ("Permissions", {
            "fields": (
                "is_staff",
                "is_superuser",
                "groups",
                "user_permissions",
            )
        }),
        ("Dates", {
            "fields": (
                "date_joined",
                "derniere_modification",
            )
        }),
    )

    readonly_fields = (
        "last_login",
        "date_joined",
        "derniere_modification",
        "tentatives_connexion",
        "derniere_connexion_ip",
    )


@admin.register(HistoriqueConnexion)
class HistoriqueConnexionAdmin(admin.ModelAdmin):

    list_display = (
        "utilisateur",
        "statut_connexion",
        "type_action",
        "date_connexion",
        "adresse_ip",
    )

    list_filter = ("statut_connexion", "type_action")
    search_fields = ("utilisateur__username", "adresse_ip")
    ordering = ("-date_connexion",)
