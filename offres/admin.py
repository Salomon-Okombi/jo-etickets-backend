# offres/admin.py
from django.contrib import admin
from .models import Offre, CategorieOffre


@admin.register(CategorieOffre)
class CategorieOffreAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "code",
        "nom",
        "nb_personnes",
        "auto_apply_all_events",
        "active",
        "ordre_affichage",
        "date_creation",
    )
    list_filter = ("active", "auto_apply_all_events")
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
        "prix",                 # prix stocké (dérivé)
        "prix_calcule_admin",   # prix recalculé (contrôle)
        "quota_billets_total",
        "quota_billets_restant",
        "packs_disponibles_admin",
        "est_disponible_admin",
        "statut",
        "date_debut_vente",
        "date_fin_vente",
        "date_creation",
    )

    list_filter = ("statut", "categorie", "evenement")
    search_fields = (
        "nom_offre",
        "evenement__nom_evenement",
        "categorie__code",
        "categorie__nom",
    )
    ordering = ("-date_creation",)

    # prix dérivé + champs système en lecture seule
    readonly_fields = ("prix", "date_creation", "date_modification")

    # perf
    list_select_related = ("evenement", "categorie", "createur")
    autocomplete_fields = ("evenement", "categorie", "createur")

    def prix_calcule_admin(self, obj: Offre):
        """
        Affiche le prix calculé depuis prix_base événement × nb_personnes catégorie.
        """
        try:
            return obj.prix_calcule
        except Exception:
            return obj.prix

    prix_calcule_admin.short_description = "Prix calculé"
    prix_calcule_admin.admin_order_field = "prix"

    def packs_disponibles_admin(self, obj: Offre):
        """
        Affiche les packs vendables estimés à partir du quota billets restant.
        Exemple :
        - SOLO (1) : packs = quota_restant // 1
        - DUO (2) : packs = quota_restant // 2
        - FAMILLE (4) : packs = quota_restant // 4
        """
        try:
            nb = int(getattr(obj.categorie, "nb_personnes", 1) or 1)
            if nb <= 0:
                nb = 1
            return int(obj.quota_billets_restant) // nb
        except Exception:
            return "—"

    packs_disponibles_admin.short_description = "Packs dispo"

    def est_disponible_admin(self, obj: Offre):
        """
        Bool métier : statut + quota + fenêtre de vente (+ cohérence événement si ajoutée).
        """
        try:
            return bool(obj.est_disponible)
        except Exception:
            return False

    est_disponible_admin.short_description = "Disponible"
    est_disponible_admin.boolean = True
