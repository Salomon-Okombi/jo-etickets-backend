# billets/serializers.py
from rest_framework import serializers
from .models import EBillet

class EBilletSerializer(serializers.ModelSerializer):
    class Meta:
        model = EBillet
        fields = "__all__"
        read_only_fields = [
            "numero_billet", "date_achat", "cle_achat", "cle_finale", "qr_code", "statut"
        ]
