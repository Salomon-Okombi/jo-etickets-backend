# Last edited by you@example.com @ 05/06/26 19:26.
#analytics/admin
from django.contrib import admin
from .models import StatistiquesVente


@admin.register(StatistiquesVente)
class StatistiquesVenteAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "offre",
        "nombre_ventes",
        "chiffre_affaires",
        "moyenne_ventes_jour",
        "pic_ventes_heure",
        "date_derniere_maj",
    )

    # Filtres utiles pour l’admin (ajuste si besoin)
    list_filter = (
        "date_derniere_maj",
        "offre",
        "offre__evenement",
        "offre__categorie",
    )

    #  Correction : nom_evenement (et champs de recherche pratiques)
    search_fields = (
        "offre__nom_offre",
        "offre__evenement__nom_evenement",
        "offre__categorie__code",
        "offre__categorie__nom",
    )

    ordering = ("-date_derniere_maj",)

    # Les stats sont calculées automatiquement → lecture seule en admin
    readonly_fields = (
        "offre",
        "nombre_ventes",
        "chiffre_affaires",
        "moyenne_ventes_jour",
        "pic_ventes_heure",
        "date_derniere_maj",
    )

    # Perf admin : évite N+1
    list_select_related = ("offre", "offre__evenement", "offre__categorie")