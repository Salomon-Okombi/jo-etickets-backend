from django.contrib import admin
from .models import Offre


@admin.register(Offre)
class OffreAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "nom_offre",
        "evenement",
        "createur",
        "prix",
        "nb_personnes",
        "type_offre",
        "stock_disponible",
        "statut",
        "date_debut_vente",
        "date_fin_vente",
        "date_creation",
    )
    list_filter = (
        "statut",
        "type_offre",
        "evenement",
        "date_debut_vente",
        "date_fin_vente",
    )
    search_fields = (
        "nom_offre",
        "evenement__nom",
        "discipline_sportive",
        "lieu_evenement",
        "createur__email",
    )
    ordering = ("-date_creation",)
    readonly_fields = ("date_creation", "date_modification")
