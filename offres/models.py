from django.db import models
from django.conf import settings


class CategorieOffre(models.Model):
    """
    Catégorie d'offre dynamique (pilotée par l'admin).
    Exemples :
      code="SOLO", nb_personnes=1
      code="DUO", nb_personnes=2
      code="FAMILIALE", nb_personnes=4
    """
    code = models.CharField(max_length=50, unique=True)
    nom = models.CharField(max_length=120)
    description = models.TextField(blank=True, null=True)
    nb_personnes = models.PositiveIntegerField(default=1)
    cas_usage = models.TextField(blank=True, null=True)

    ordre_affichage = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)

    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "categorie_offre"
        ordering = ["ordre_affichage", "nom"]
        indexes = [
            models.Index(fields=["active"]),
            models.Index(fields=["ordre_affichage"]),
        ]

    def __str__(self):
        return f"{self.code} - {self.nom}"


class Offre(models.Model):
    STATUT_CHOICES = [
        ("ACTIVE", "Active"),
        ("INACTIVE", "Inactive"),
        ("EPUISEE", "Epuisée"),
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

    prix = models.DecimalField(max_digits=8, decimal_places=2)

    stock_total = models.PositiveIntegerField()
    stock_disponible = models.PositiveIntegerField()

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
        indexes = [
            models.Index(fields=["evenement", "statut"]),
            models.Index(fields=["categorie", "statut"]),
        ]
        constraints = [
            # Une seule offre par (événement, catégorie)
            models.UniqueConstraint(fields=["evenement", "categorie"], name="uniq_evenement_categorie"),
        ]

    def __str__(self):
        return f"{self.nom_offre} ({self.evenement})"

    @property
    def nb_personnes(self) -> int:
        return int(self.categorie.nb_personnes or 1)

    @property
    def type_offre(self) -> str:
        # Compat : ce que le frontend appelait "type_offre"
        return self.categorie.code