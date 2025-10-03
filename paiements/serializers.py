# paiements/serializers.py
from rest_framework import serializers
from paiements.models import Commande
from paniers.models import Panier

class CommandeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Commande
        fields = [
            "id",
            "utilisateur",
            "panier",
            "numero_commande",
            "date_commande",
            "montant_total",
            "statut_paiement",
            "methode_paiement",
            "reference_paiement",
            "date_paiement",
        ]
        read_only_fields = ["utilisateur", "numero_commande", "date_commande", "montant_total"]

    def validate_panier(self, value):
        if not value.lignes.exists():
            raise serializers.ValidationError("Le panier est vide, impossible de créer une commande.")
        return value
