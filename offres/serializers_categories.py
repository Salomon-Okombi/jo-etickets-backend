#offres/serializers_categories.py
from rest_framework import serializers
from .models import CategorieOffre


class CategorieOffreSerializer(serializers.ModelSerializer):
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
            "date_creation",
            "date_modification",
        ]
        read_only_fields = ["date_creation", "date_modification"]