from rest_framework import serializers
from .models import Evenement


class EvenementSerializer(serializers.ModelSerializer):
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
            "date_creation",
        ]
        read_only_fields = ["id", "date_creation"]