from rest_framework import serializers
from .models import CategorieOffre


class CategorieOffreSerializer(serializers.ModelSerializer):
    """
    Serializer public/admin pour les catégories d’offres
    (SOLO, DUO, FAMILLE…)
    """

    class Meta:
        model = CategorieOffre
        fields = [
            "id",
            "code",
            "nom",
            "description",
            "nb_personnes",
            "cas_usage",
            "ordre_affichage",
            "active",
            "auto_apply_all_events",  # <-- AJOUT IMPORTANT
            "date_creation",
            "date_modification",
        ]
        read_only_fields = [
            "date_creation",
            "date_modification",
        ]