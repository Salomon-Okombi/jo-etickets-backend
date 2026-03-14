from django.contrib import admin
from .models import Commande, LigneCommande


class LigneCommandeInline(admin.TabularInline):
    model = LigneCommande
    extra = 0
    fields = ("offre", "quantite", "prix_unitaire", "sous_total")
    readonly_fields = ("prix_unitaire", "sous_total")


@admin.register(Commande)
class CommandeAdmin(admin.ModelAdmin):
    list_display = (
        "numero_commande",
        "utilisateur",
        "statut",
        "total",
        "date_creation",
        "date_paiement",
        "reference_paiement",
    )

    list_filter = ("statut", "date_creation", "date_paiement")
    search_fields = ("numero_commande", "utilisateur__email", "utilisateur__username")
    ordering = ("-date_creation",)

    inlines = [LigneCommandeInline]

    readonly_fields = (
        "numero_commande",
        "total",
        "date_creation",
        "date_paiement",
        "reference_paiement",
    )