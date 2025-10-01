from django.contrib import admin
from .models import Commande


@admin.register(Commande)
class CommandeAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "numero_commande",
        "utilisateur",
        "panier",
        "montant_total",
        "statut_paiement",
        "methode_paiement",
        "date_commande",
        "date_paiement",
    )
    list_filter = ("statut_paiement", "date_commande", "methode_paiement")
    search_fields = ("numero_commande", "utilisateur__email", "utilisateur__nom_utilisateur")
    ordering = ("-date_commande",)
    readonly_fields = ("numero_commande", "date_commande")
