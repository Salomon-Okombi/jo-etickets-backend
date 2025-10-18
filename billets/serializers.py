# billets/serializers.py
from rest_framework import serializers
from .models import EBillet

class EBilletSerializer(serializers.ModelSerializer):
    """
    Serializer sécurisé pour EBillet :
    - N'EXPOSE PAS les champs sensibles: cle_achat, cle_finale
    - qr_code est en lecture seule (base64), utile pour l'affichage/téléchargement
    - numero_billet, date_achat, statut et validateur sont en lecture seule
    """
    class Meta:
        model = EBillet
        fields = [
            "id",
            "numero_billet",
            "utilisateur",
            "offre",
            "validateur",
            "date_achat",
            "prix_paye",
            "statut",
            "date_utilisation",
            "lieu_utilisation",
            "qr_code",
        ]
        read_only_fields = [
            "numero_billet",
            "date_achat",
            "qr_code",
            "statut",
            "validateur",
        ]
