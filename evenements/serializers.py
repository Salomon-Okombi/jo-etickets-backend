from rest_framework import serializers
from .models import Evenement


class EvenementListSerializer(serializers.ModelSerializer):
    image_url = serializers.ReadOnlyField()

    class Meta:
        model = Evenement
        fields = [
            "id",
            "nom_evenement",
            "description_courte",
            "image_url",
            "date_evenement",
            "heure_evenement",
            "lieu",
            "discipline",
        ]


class EvenementDetailSerializer(serializers.ModelSerializer):
    image_url = serializers.ReadOnlyField()

    class Meta:
        model = Evenement
        fields = [
            "id",
            "nom_evenement",
            "description_longue",
            "image_url",
            "date_evenement",
            "heure_evenement",
            "lieu",
            "discipline",
            "statut",
        ]