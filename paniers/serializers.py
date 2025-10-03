# paniers/serializers.py
from rest_framework import serializers
from .models import Panier, LignePanier

class LignePanierSerializer(serializers.ModelSerializer):
    prix_unitaire = serializers.DecimalField(max_digits=8, decimal_places=2, read_only=True)
    sous_total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = LignePanier
        fields = ["id", "offre", "quantite", "prix_unitaire", "sous_total", "date_ajout"]
        read_only_fields = ["id", "prix_unitaire", "sous_total", "date_ajout"]

class PanierSerializer(serializers.ModelSerializer):
    lignes = LignePanierSerializer(many=True, read_only=True)
    montant_total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Panier
        fields = ["id", "utilisateur", "statut", "date_creation", "date_expiration", "montant_total", "lignes"]
        read_only_fields = ["id", "utilisateur", "date_creation", "montant_total", "lignes"]
