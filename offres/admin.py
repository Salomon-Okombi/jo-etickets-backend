#offres/admin
from django.contrib import admin
from .models import Offre, CategorieOffre


@admin.register(CategorieOffre)
class CategorieOffreAdmin(admin.ModelAdmin):
    list_display = ("id", "code", "nom", "nb_personnes", "active", "ordre_affichage", "date_creation")
    list_filter = ("active",)
    search_fields = ("code", "nom")
    ordering = ("ordre_affichage", "nom")
    readonly_fields = ("date_creation", "date_modification")


@admin.register(Offre)
class OffreAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "nom_offre",
        "evenement",
        "categorie",
        "prix",
        "stock_disponible",
        "statut",
        "date_debut_vente",
        "date_fin_vente",
        "date_creation",
    )
    list_filter = ("statut", "categorie", "evenement")
    search_fields = ("nom_offre", "evenement__nom_evenement", "categorie__code", "categorie__nom")
    ordering = ("-date_creation",)
    readonly_fields = ("date_creation", "date_modification")
