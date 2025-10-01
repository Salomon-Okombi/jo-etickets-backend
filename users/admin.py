from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Utilisateur, HistoriqueConnexion


@admin.register(Utilisateur)
class UtilisateurAdmin(UserAdmin):
    # colonnes affichées dans la liste
    list_display = (
        "username",
        "email",
        "type_compte",
        "statut",
        "date_creation",
        "derniere_connexion",
        "tentatives_connexion",
    )
    list_filter = ("type_compte", "statut", "is_staff", "is_superuser", "is_active")
    search_fields = ("username", "email", "cle_utilisateur")
    ordering = ("-date_creation",)

    # champs affichés dans le détail
    fieldsets = UserAdmin.fieldsets + (
        ("Informations supplémentaires", {
            "fields": (
                "type_compte",
                "statut",
                "cle_utilisateur",
                "date_creation",
                "derniere_connexion",
                "tentatives_connexion",
                "token_reset_mdp",
                "date_token_reset",
            )
        }),
    )

    readonly_fields = ("cle_utilisateur", "date_creation", "derniere_connexion")


@admin.register(HistoriqueConnexion)
class HistoriqueConnexionAdmin(admin.ModelAdmin):
    list_display = (
        "utilisateur",
        "date_connexion",
        "adresse_ip",
        "statut_connexion",
        "type_action",
    )
    list_filter = ("statut_connexion", "type_action", "date_connexion")
    search_fields = ("utilisateur__username", "utilisateur__email", "adresse_ip")
    ordering = ("-date_connexion",)
    readonly_fields = ("date_connexion",)

