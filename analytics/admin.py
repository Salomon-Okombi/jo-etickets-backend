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
    list_filter = ("date_derniere_maj",)
    search_fields = ("offre__nom_offre", "offre__evenement__nom")
    ordering = ("-date_derniere_maj",)
    readonly_fields = ("date_derniere_maj",)
