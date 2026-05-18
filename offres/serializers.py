# offres/serializers.py
from decimal import Decimal, InvalidOperation
from django.utils import timezone
from rest_framework import serializers
from .models import Offre


class OffrePublicSerializer(serializers.ModelSerializer):
    evenement_nom = serializers.CharField(source="evenement.nom_evenement", read_only=True)
    categorie_code = serializers.CharField(source="categorie.code", read_only=True)
    categorie_nom = serializers.CharField(source="categorie.nom", read_only=True)

    nb_personnes = serializers.IntegerField(source="categorie.nb_personnes", read_only=True)

    multiplicateur = serializers.SerializerMethodField()
    prix_calcule = serializers.SerializerMethodField()
    est_disponible = serializers.SerializerMethodField()

    type_offre = serializers.CharField(source="categorie.code", read_only=True)

    # Quotas billets + packs
    quota_billets_total = serializers.IntegerField(read_only=True)
    quota_billets_restant = serializers.IntegerField(read_only=True)
    packs_total = serializers.SerializerMethodField()
    packs_disponibles = serializers.SerializerMethodField()

    class Meta:
        model = Offre
        fields = [
            "id",
            "evenement",
            "evenement_nom",
            "categorie",
            "categorie_code",
            "categorie_nom",
            "nom_offre",
            "description",
            "prix_calcule",
            "multiplicateur",
            "type_offre",
            "nb_personnes",

            "quota_billets_total",
            "quota_billets_restant",
            "packs_total",
            "packs_disponibles",

            "date_debut_vente",
            "date_fin_vente",
            "statut",
            "est_disponible",
        ]

    def get_multiplicateur(self, obj: Offre):
        try:
            return int(getattr(obj, "multiplicateur"))
        except Exception:
            try:
                return int(obj.categorie.nb_personnes or 1)
            except Exception:
                return 1

    def get_prix_calcule(self, obj: Offre):
        """
        Toujours renvoyer une string '0.00' au pire, pour éviter les 500.
        """
        try:
            val = getattr(obj, "prix_calcule", None)
            if val is None:
                return "0.00"
            return str(Decimal(val).quantize(Decimal("0.01")))
        except (InvalidOperation, Exception):
            return "0.00"

    def get_est_disponible(self, obj: Offre):
        try:
            return bool(getattr(obj, "est_disponible"))
        except Exception:
            return False

    def get_packs_total(self, obj: Offre):
        try:
            return int(getattr(obj, "packs_total"))
        except Exception:
            try:
                nb = int(obj.categorie.nb_personnes or 1)
                return int(obj.quota_billets_total) // max(nb, 1)
            except Exception:
                return 0

    def get_packs_disponibles(self, obj: Offre):
        try:
            return int(getattr(obj, "packs_disponibles"))
        except Exception:
            try:
                nb = int(obj.categorie.nb_personnes or 1)
                return int(obj.quota_billets_restant) // max(nb, 1)
            except Exception:
                return 0


class OffreAdminSerializer(serializers.ModelSerializer):
    """
    Admin : pas de prix en entrée (prix dérivé).
    L’admin manipule :
    - evenement, categorie
    - quota billets (total/restant)
    - fenêtre de vente
    - statut, nom, description

    On renvoie aussi des champs read-only utiles pour l’UI admin.
    """
    evenement_nom = serializers.CharField(source="evenement.nom_evenement", read_only=True)
    categorie_code = serializers.CharField(source="categorie.code", read_only=True)
    categorie_nom = serializers.CharField(source="categorie.nom", read_only=True)

    nb_personnes = serializers.IntegerField(source="categorie.nb_personnes", read_only=True)
    multiplicateur = serializers.SerializerMethodField()
    prix_calcule = serializers.SerializerMethodField()
    est_disponible = serializers.SerializerMethodField()

    packs_total = serializers.SerializerMethodField()
    packs_disponibles = serializers.SerializerMethodField()

    class Meta:
        model = Offre
        fields = [
            "id",
            "evenement",
            "evenement_nom",
            "categorie",
            "categorie_code",
            "categorie_nom",
            "nom_offre",
            "description",

            # Quotas en billets (saisie admin)
            "quota_billets_total",
            "quota_billets_restant",

            "date_debut_vente",
            "date_fin_vente",
            "statut",

            # read-only utiles
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

    def get_multiplicateur(self, obj: Offre):
        try:
            return int(getattr(obj, "multiplicateur"))
        except Exception:
            try:
                return int(obj.categorie.nb_personnes or 1)
            except Exception:
                return 1

    def get_prix_calcule(self, obj: Offre):
        try:
            val = getattr(obj, "prix_calcule", None)
            if val is None:
                return "0.00"
            return str(Decimal(val).quantize(Decimal("0.01")))
        except (InvalidOperation, Exception):
            return "0.00"

    def get_est_disponible(self, obj: Offre):
        try:
            return bool(getattr(obj, "est_disponible"))
        except Exception:
            return False

    def get_packs_total(self, obj: Offre):
        try:
            return int(getattr(obj, "packs_total"))
        except Exception:
            return 0

    def get_packs_disponibles(self, obj: Offre):
        try:
            return int(getattr(obj, "packs_disponibles"))
        except Exception:
            return 0

    def validate(self, attrs):
        """
        Validations admin :
        - cohérence quota billets
        - cohérence fenêtre de vente
        - cohérence avec dates de l'événement
        """
        instance = getattr(self, "instance", None)

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

        # cohérence avec l'événement
        evenement = attrs.get("evenement", getattr(instance, "evenement", None))
        if evenement and fin:
            try:
                if getattr(evenement, "date_fin", None) and fin > evenement.date_fin:
                    raise serializers.ValidationError(
                        {"date_fin_vente": "La fin de vente ne peut pas dépasser la fin de l’événement."}
                    )
            except Exception:
                pass

        # optionnel : empêcher de créer une offre déjà expirée
        if instance is None and fin and fin < timezone.now():
            raise serializers.ValidationError(
                {"date_fin_vente": "Impossible de créer une offre déjà expirée."}
            )

        return attrs