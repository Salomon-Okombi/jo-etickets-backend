from decimal import Decimal
from django.db import models
from django.conf import settings
from django.utils import timezone


class CategorieOffre(models.Model):
    """
    Catégorie d’offre (template) :
    - SOLO (1 personne)
    - DUO (2 personnes)
    - FAMILLE (4 personnes)
    """

    code = models.CharField(max_length=50, unique=True)
    nom = models.CharField(max_length=120)
    description = models.TextField(blank=True, null=True)

    # Multiplicateur métier (packs quantité)
    nb_personnes = models.PositiveIntegerField(default=1)

    cas_usage = models.TextField(blank=True, null=True)

    ordre_affichage = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)

    # Nouveau : catégorie globale (auto ajoutée à tous les événements)
    auto_apply_all_events = models.BooleanField(
        default=True,
        help_text="Si True, cette catégorie est appliquée automatiquement à tous les événements (SOLO/DUO/FAMILLE). "
                  "Si False, elle est créée seulement pour des événements spécifiques."
    )

    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "categorie_offre"
        ordering = ["ordre_affichage", "nom"]
        indexes = [
            models.Index(fields=["active"]),
            models.Index(fields=["ordre_affichage"]),
            models.Index(fields=["auto_apply_all_events"]),
        ]

    def __str__(self) -> str:
        return f"{self.code} - {self.nom}"


class Offre(models.Model):
    """
    Offre vendable associée à :
    - un événement
    - une catégorie (SOLO / DUO / FAMILLE)
    La capacité est gérée en QUOTA DE BILLETS (places).
    """

    STATUT_CHOICES = [
        ("ACTIVE", "Active"),
        ("INACTIVE", "Inactive"),
        ("EPUISEE", "Épuisée"),
        ("EXPIREE", "Expirée"),
    ]

    evenement = models.ForeignKey(
        "evenements.Evenement",
        on_delete=models.CASCADE,
        related_name="offres",
    )

    categorie = models.ForeignKey(
        "offres.CategorieOffre",
        on_delete=models.PROTECT,
        related_name="offres",
    )

    createur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="offres_creees",
    )

    nom_offre = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    # Prix dérivé (stocké)
    prix = models.DecimalField(max_digits=10, decimal_places=2)

    # Nouveau : quota en billets (places)
    quota_billets_total = models.PositiveIntegerField(
        default=0,
        help_text="Nombre total de billets vendables pour cette catégorie sur cet événement."
    )
    quota_billets_restant = models.PositiveIntegerField(
        default=0,
        help_text="Nombre de billets restants vendables pour cette catégorie sur cet événement."
    )

    date_debut_vente = models.DateTimeField()
    date_fin_vente = models.DateTimeField()

    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default="ACTIVE",
    )

    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "offre"
        ordering = ["date_creation"]
        indexes = [
            models.Index(fields=["evenement", "statut"]),
            models.Index(fields=["categorie", "statut"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["evenement", "categorie"],
                name="uniq_evenement_categorie",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.nom_offre} ({self.evenement})"

    # ======================================================
    # PROPRIÉTÉS MÉTIER
    # ======================================================

    @property
    def nb_personnes(self) -> int:
        """
        Nombre de billets consommés par 1 pack :
        SOLO=1, DUO=2, FAMILLE=4
        """
        try:
            return int(self.categorie.nb_personnes or 1)
        except Exception:
            return 1

    @property
    def multiplicateur(self) -> int:
        return self.nb_personnes

    @property
    def type_offre(self) -> str:
        try:
            return self.categorie.code
        except Exception:
            return ""

    # Quota exprimé en packs (dérivé du quota billets)
    @property
    def packs_total(self) -> int:
        nb = self.nb_personnes or 1
        return int(self.quota_billets_total) // nb

    @property
    def packs_disponibles(self) -> int:
        nb = self.nb_personnes or 1
        return int(self.quota_billets_restant) // nb

    # ======================================================
    # PRIX
    # ======================================================

    def compute_prix_calcule(self) -> Decimal:
        """
        Prix final du pack :
        prix_base événement × nb_personnes catégorie
        """
        base = getattr(self.evenement, "prix_base", Decimal("0.00")) or Decimal("0.00")
        return (Decimal(base) * Decimal(self.multiplicateur)).quantize(Decimal("0.01"))

    @property
    def prix_calcule(self) -> Decimal:
        return self.compute_prix_calcule()

    # ======================================================
    # DISPONIBILITÉ
    # ======================================================

    @property
    def est_disponible(self) -> bool:
        """
        Disponible si :
        - statut ACTIVE
        - packs_disponibles > 0
        - dans la fenêtre de vente
        - (optionnel mais cohérent) événement publié et non expiré
        """
        if self.statut != "ACTIVE":
            return False

        if self.packs_disponibles <= 0:
            return False

        now = timezone.now()

        if self.date_debut_vente and now < self.date_debut_vente:
            return False

        if self.date_fin_vente and now > self.date_fin_vente:
            return False

        # Cohérence avec l'événement (recommandé)
        try:
            if getattr(self.evenement, "statut", None) != "PUBLIE":
                return False
            if getattr(self.evenement, "date_fin", None) and now > self.evenement.date_fin:
                return False
        except Exception:
            pass

        return True

    # ======================================================
    # VALIDATIONS / SAUVEGARDE
    # ======================================================

    def clean(self):
        if self.date_debut_vente and self.date_fin_vente:
            if self.date_debut_vente >= self.date_fin_vente:
                raise ValueError("date_fin_vente doit être postérieure à date_debut_vente.")

        # Quotas cohérents
        if self.quota_billets_restant > self.quota_billets_total:
            self.quota_billets_restant = self.quota_billets_total

        # Optionnel : éviter des quotas non multiples du pack
        # (si tu veux que DUO consomme toujours 2 billets, FAMILLE 4)
        nb = self.nb_personnes or 1
        if nb > 1:
            # On ne force pas, mais tu peux décider de forcer l'arrondi inférieur :
            # self.quota_billets_total = (self.quota_billets_total // nb) * nb
            # self.quota_billets_restant = min(self.quota_billets_restant, self.quota_billets_total)
            pass

    def save(self, *args, **kwargs):
        # Prix toujours recalculé
        self.prix = self.compute_prix_calcule()

        # Quota restant plafonné
        if self.quota_billets_restant > self.quota_billets_total:
            self.quota_billets_restant = self.quota_billets_total

        super().save(*args, **kwargs)