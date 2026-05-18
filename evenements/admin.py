# evenements/admin.py
from django.contrib import admin
from django.utils import timezone
from datetime import timedelta

from .models import Evenement
from offres.models import CategorieOffre, Offre


DEFAULT_QUOTA_BILLETS = 100  # quota par défaut en billets (à ajuster)
DEFAULT_DAYS = 60


@admin.register(Evenement)
class EvenementAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "nom_evenement",
        "discipline",
        "lieu",
        "date_debut",
        "date_fin",
        "prix_base",
        "statut",
    )

    list_filter = (
        "statut",
        "discipline",
        "date_debut",
        "date_fin",
    )

    search_fields = (
        "nom_evenement",
        "description_courte",
        "description_longue",
        "lieu",
    )

    ordering = ("date_debut",)

    readonly_fields = ("date_creation",)

    fieldsets = (
        ("Informations principales", {
            "fields": (
                "nom_evenement",
                "statut",
                "discipline",
                "lieu",
            )
        }),
        ("Période de l’événement", {
            "description": (
                "L’événement est visible et réservable uniquement pendant cette période. "
                "À la date de fin, il sera automatiquement archivé."
            ),
            "fields": (
                "date_debut",
                "date_fin",
            )
        }),
        ("Tarification", {
            "description": (
                "Prix de base SOLO. "
                "Les catégories (DUO, FAMILLE…) appliquent un multiplicateur."
            ),
            "fields": ("prix_base",)
        }),
        ("Contenu boutique", {
            "fields": (
                "image",
                "description_courte",
                "description_longue",
            )
        }),
        ("Système", {
            "fields": ("date_creation",)
        }),
    )

    def save_model(self, request, obj, form, change):
        """
        Lorsqu’un événement est créé via l’admin Django,
        on génère automatiquement les offres pour chaque catégorie GLOBALE active.
        (SOLO/DUO/FAMILLE par défaut)
        """
        is_new = obj.pk is None
        super().save_model(request, obj, form, change)

        if not is_new:
            return

        start = timezone.now() - timedelta(minutes=5)
        end = timezone.now() + timedelta(days=DEFAULT_DAYS)

        # IMPORTANT : seulement les catégories globales
        categories = (
            CategorieOffre.objects
            .filter(active=True, auto_apply_all_events=True)
            .order_by("ordre_affichage", "nom")
        )

        for cat in categories:
            Offre.objects.get_or_create(
                evenement=obj,
                categorie=cat,
                defaults={
                    "createur": request.user,
                    "nom_offre": f"{cat.code} - {obj.nom_evenement}",
                    "description": cat.description or "",
                    # Quota en billets (pas de stock en packs)
                    "quota_billets_total": DEFAULT_QUOTA_BILLETS,
                    "quota_billets_restant": DEFAULT_QUOTA_BILLETS,
                    "date_debut_vente": start,
                    "date_fin_vente": end,
                    "statut": "ACTIVE",
                },
            )