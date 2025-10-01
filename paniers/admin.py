from django.contrib import admin
from .models import Panier, LignePanier


class LignePanierInline(admin.TabularInline):
    model = LignePanier
    extra = 1
    fields = ("offre", "quantite", "prix_unitaire", "sous_total")
    readonly_fields = ("sous_total",)


@admin.register(Panier)
class PanierAdmin(admin.ModelAdmin):
    list_display = ("id", "utilisateur", "statut", "montant_total", "date_creation", "date_expiration")
    list_filter = ("statut", "date_creation")
    search_fields = ("utilisateur__email", "utilisateur__nom")
    inlines = [LignePanierInline]


@admin.register(LignePanier)
class LignePanierAdmin(admin.ModelAdmin):
    list_display = ("id", "panier", "offre", "quantite", "prix_unitaire", "sous_total", "date_ajout")
    list_filter = ("offre", "date_ajout")
    search_fields = ("offre__nom_offre", "panier__utilisateur__email")
