from django.contrib import admin
from .models import Paiement


@admin.register(Paiement)
class PaiementAdmin(admin.ModelAdmin):
    list_display = (
        "reference",
        "utilisateur",
        "commande",
        "montant",
        "statut",
        "provider",
        "date_creation",
        "date_confirmation",
    )
    list_filter = ("statut", "provider", "date_creation")
    search_fields = ("reference", "commande__numero_commande", "utilisateur__email", "utilisateur__username")
    ordering = ("-date_creation",)
    readonly_fields = ("reference", "date_creation", "date_confirmation")