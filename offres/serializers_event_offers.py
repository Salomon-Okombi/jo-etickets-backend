# offres/serializers_event_offers.py
from decimal import Decimal, InvalidOperation
from django.utils import timezone
from rest_framework import serializers

from .models import Offre


class EventOfferAdminSerializer(serializers.ModelSerializer):
    """
    Serializer admin pour gérer les offres d'un événement (event-offers).
    L'offre = (événement × catégorie) + quotas billets + fenêtre de vente + statut.
    Prix toujours dérivé (prix_base × nb_personnes).
    """

    # Libellés utiles
    evenement_nom = serializers.CharField(source="evenement.nom_evenement", read_only=True)
    categorie_code = serializers.CharField(source="categorie.code", read_only=True)
    categorie_nom = serializers.CharField(source="categorie.nom", read_only=True)

    # Infos catégorie en lecture
    nb_personnes = serializers.IntegerField(source="categorie.nb_personnes", read_only=True)

    # Calculs
    multiplicateur = serializers.SerializerMethodField()
    prix_calcule = serializers.SerializerMethodField()
    packs_total = serializers.SerializerMethodField()
    packs_disponibles = serializers.SerializerMethodField()
    est_disponible = serializers.SerializerMethodField()

    class Meta:
        model = Offre
        fields = [
            "id",

            # clés
            "evenement",
            "evenement_nom",
            "categorie",
            "categorie_code",
            "categorie_nom",

            # contenu
            "nom_offre",
            "description",

            # quotas en billets (saisie admin)
            "quota_billets_total",
            "quota_billets_restant",

            # fenêtre de vente + statut
            "date_debut_vente",
            "date_fin_vente",
            "statut",

            # infos calculées (read-only)
            "prix_calcule",
            "multiplicateur",
            "nb_personnes",
            "packs_total",
            "packs_disponibles",
            "est_disponible",
        ]

        read_only_fields = [
            "evenement_nom",
            "categorie_code",
            "categorie_nom",
            "prix_calcule",
            "multiplicateur",
            "nb_personnes",
            "packs_total",
            "packs_disponibles",
            "est_disponible",
        ]

    def get_multiplicateur(self, obj: Offre) -> int:
        try:
            return int(getattr(obj, "multiplicateur"))
        except Exception:
            try:
                return int(obj.categorie.nb_personnes or 1)
            except Exception:
                return 1

    def get_prix_calcule(self, obj: Offre) -> str:
        """
        Toujours renvoyer une string '0.00' (DRF Decimal en string).
        """
        try:
            val = getattr(obj, "prix_calcule", None)
            if val is None:
                return "0.00"
            return str(Decimal(val).quantize(Decimal("0.01")))
        except (InvalidOperation, Exception):
            return "0.00"

    def get_packs_total(self, obj: Offre) -> int:
        try:
            return int(getattr(obj, "packs_total"))
        except Exception:
            nb = self.get_multiplicateur(obj) or 1
            return int(obj.quota_billets_total) // max(nb, 1)

    def get_packs_disponibles(self, obj: Offre) -> int:
        try:
            return int(getattr(obj, "packs_disponibles"))
        except Exception:
            nb = self.get_multiplicateur(obj) or 1
            return int(obj.quota_billets_restant) // max(nb, 1)

    def get_est_disponible(self, obj: Offre) -> bool:
        try:
            return bool(getattr(obj, "est_disponible"))
        except Exception:
            return False

    def validate(self, attrs):
        """
        Validations admin :
        - quota_restant <= quota_total
        - date_fin_vente > date_debut_vente
        - date_fin_vente <= fin événement (cohérence)
        - (recommandé) quotas multiples de nb_personnes pour éviter des billets "perdus"
        """
        instance = getattr(self, "instance", None)

        evenement = attrs.get("evenement", getattr(instance, "evenement", None))
        categorie = attrs.get("categorie", getattr(instance, "categorie", None))

        quota_total = attrs.get("quota_billets_total", getattr(instance, "quota_billets_total", None))
        quota_restant = attrs.get("quota_billets_restant", getattr(instance, "quota_billets_restant", None))

        if quota_total is not None and quota_restant is not None:
            if quota_restant > quota_total:
                raise serializers.ValidationError(
                    {"quota_billets_restant": "Le quota restant ne peut pas dépasser le quota total."}
                )

        debut = attrs.get("date_debut_vente", getattr(instance, "date_debut_vente", None))
        fin = attrs.get("date_fin_vente", getattr(instance, "date_fin_vente", None))

        if debut and fin and debut >= fin:
            raise serializers.ValidationError(
                {"date_fin_vente": "La fin de vente doit être postérieure au début de vente."}
            )

        # Cohérence avec dates de l'événement
        if evenement and fin:
            try:
                if getattr(evenement, "date_fin", None) and fin > evenement.date_fin:
                    raise serializers.ValidationError(
                        {"date_fin_vente": "La fin de vente ne peut pas dépasser la fin de l’événement."}
                    )
            except Exception:
                pass

        # Optionnel : empêcher création d'une offre déjà expirée
        if instance is None and fin and fin < timezone.now():
            raise serializers.ValidationError(
                {"date_fin_vente": "Impossible de créer une offre déjà expirée."}
            )

        # Recommandé : quota multiple du pack (DUO=2, FAMILLE=4)
        try:
            nb = int(getattr(categorie, "nb_personnes", 1) or 1)
        except Exception:
            nb = 1

        if nb <= 0:
            nb = 1

        if quota_total is not None and nb > 1 and (int(quota_total) % nb != 0):
            raise serializers.ValidationError(
                {"quota_billets_total": f"Le quota total doit être multiple de {nb} (taille du pack)."}
            )

        if quota_restant is not None and nb > 1 and (int(quota_restant) % nb != 0):
            raise serializers.ValidationError(
                {"quota_billets_restant": f"Le quota restant doit être multiple de {nb} (taille du pack)."}
            )

        return attrs
