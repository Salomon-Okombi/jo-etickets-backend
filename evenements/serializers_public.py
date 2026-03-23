# evenements/serializers_public.py
from rest_framework import serializers
from evenements.models import Evenement

class PublicEvenementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Evenement
        fields = [
            "id",
            "nom",
            "discipline_sportive",
            "date_evenement",
            "lieu_evenement",
            "description",
            "statut",
        ]