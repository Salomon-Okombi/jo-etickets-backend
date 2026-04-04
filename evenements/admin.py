from django.contrib import admin
from .models import Evenement


@admin.register(Evenement)
class EvenementAdmin(admin.ModelAdmin):

    list_display = (
        "nom_evenement",
        "discipline",
        "lieu",
        "date_evenement",
        "statut",
    )

    list_filter = (
        "statut",
        "discipline",
        "date_evenement",
    )

    search_fields = (
        "nom_evenement",
        "description_courte",
        "description_longue",
        "lieu",
    )

    ordering = (
        "date_evenement",
    )

    readonly_fields = (
        "date_creation",
    )

    fieldsets = (
        ("Informations principales", {
            "fields": (
                "nom_evenement",
                "statut",
                "discipline",
                "lieu",
                "date_evenement",
                "heure_evenement",
            )
        }),
        ("Contenu boutique", {
            "fields": (
                "image",
                "description_courte",
                "description_longue",
            )
        }),
        ("Système", {
            "fields": (
                "date_creation",
            )
        }),
    )