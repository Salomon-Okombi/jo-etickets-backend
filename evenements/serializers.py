# evenements/serializers.py
from rest_framework import serializers
from .models import Evenement

class EvenementAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Evenement
        fields = [
            "id",
            "nom_evenement",
            "discipline",
            "date_evenement",
            "lieu",
            "description_courte",
            "description_longue",
            "image",
            "statut",
        ]