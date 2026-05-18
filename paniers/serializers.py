#paniers : serializers
from rest_framework import serializers
from .models import Panier, LignePanier


class LignePanierSerializer(serializers.ModelSerializer):
    class Meta:
        model = LignePanier
        fields = ["id", "offre", "quantite", "prix_unitaire", "sous_total", "date_ajout"]
        read_only_fields = ["prix_unitaire", "sous_total", "date_ajout"]


class PanierSerializer(serializers.ModelSerializer):
    lignes = LignePanierSerializer(many=True, read_only=True)

    class Meta:
        model = Panier
        fields = ["id", "statut", "montant_total", "lignes", "date_creation", "date_modification"]
        read_only_fields = ["montant_total", "date_creation", "date_modification"]
