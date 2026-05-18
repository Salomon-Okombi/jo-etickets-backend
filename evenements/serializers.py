from django.utils import timezone
from rest_framework import serializers
from .models import Evenement


def build_image_url(request, obj) -> str | None:
    """
    Retourne l'URL de l'image :
    - absolue si request est disponible
    - None si pas d'image
    """
    if not getattr(obj, "image", None):
        return None
    if request:
        return request.build_absolute_uri(obj.image.url)
    return None


# ============================================================
# LISTE PUBLIQUE DES ÉVÉNEMENTS (CARTE / LISTING)
# ============================================================

class EvenementListSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Evenement
        fields = [
            "id",
            "nom_evenement",
            "discipline",
            "lieu",
            "date_debut",
            "date_fin",
            "description_courte",
            "image_url",
            "prix_base",
        ]

    def get_image_url(self, obj):
        request = self.context.get("request")
        return build_image_url(request, obj)


# ============================================================
# DÉTAIL D’UN ÉVÉNEMENT (PAGE DÉTAIL PUBLIQUE)
# ============================================================

class EvenementDetailSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Evenement
        fields = [
            "id",
            "nom_evenement",
            "discipline",
            "lieu",
            "date_debut",
            "date_fin",
            "description_longue",
            "image_url",
            "prix_base",
        ]

    def get_image_url(self, obj):
        request = self.context.get("request")
        return build_image_url(request, obj)


# ============================================================
# ADMIN (CRUD COMPLET)
# ============================================================

class EvenementAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Evenement
        fields = [
            "id",
            "nom_evenement",
            "discipline",
            "lieu",
            "date_debut",
            "date_fin",
            "prix_base",
            "description_courte",
            "description_longue",
            "image",
            "statut",
        ]

    def validate(self, attrs):
        """
        Règles métier ADMIN :
        - date_fin > date_debut
        - on ne peut pas créer un événement dans le passé
        - on peut modifier un événement déjà en cours
        """
        debut = attrs.get("date_debut")
        fin = attrs.get("date_fin")
        now = timezone.now()

        # date_fin après date_debut
        if debut and fin and debut >= fin:
            raise serializers.ValidationError(
                "La date de fin doit être postérieure à la date de début."
            )

        # bloquer uniquement à la création
        if self.instance is None and debut and debut < now:
            raise serializers.ValidationError(
                "Impossible de créer un événement dans le passé."
            )

        return attrs


# ============================================================
# PAGE D’ACCUEIL – TOP 3 ÉVÉNEMENTS
# ============================================================

class EvenementHomeSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Evenement
        fields = [
            "id",
            "nom_evenement",
            "description_courte",
            "image_url",
            "lieu",
            "date_debut",
            "discipline",
        ]

    def get_image_url(self, obj):
        request = self.context.get("request")
        return build_image_url(request, obj)
