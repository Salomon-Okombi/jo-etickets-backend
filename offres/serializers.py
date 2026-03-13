# offres/serializers.py
from rest_framework import serializers
from .models import Offre

class OffreSerializer(serializers.ModelSerializer):
    evenement_nom = serializers.CharField(source="evenement.nom", read_only=True)

    class Meta:
        model = Offre
        fields = "__all__"
        read_only_fields = ["createur", "date_creation", "date_modification", "evenement_nom"]