# offres/serializers.py
from rest_framework import serializers
from .models import Offre

class OffreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Offre
        fields = "__all__"
        read_only_fields = ["createur", "date_creation", "date_modification"]
