from rest_framework import serializers
from .models import Commande, LigneCommande
from offres.models import Offre


class LigneCommandeSerializer(serializers.ModelSerializer):
    offre_nom = serializers.CharField(source="offre.nom_offre", read_only=True)

    class Meta:
        model = LigneCommande
        fields = ["id", "offre", "offre_nom", "quantite", "prix_unitaire", "sous_total"]
        read_only_fields = ["prix_unitaire", "sous_total", "offre_nom"]


class CommandeSerializer(serializers.ModelSerializer):
    lignes = LigneCommandeSerializer(many=True, read_only=True)
    utilisateur_nom = serializers.SerializerMethodField()

    class Meta:
        model = Commande
        fields = [
            "id",
            "numero_commande",
            "utilisateur",
            "utilisateur_nom",
            "statut",
            "total",
            "date_creation",
            "date_paiement",
            "reference_paiement",
            "lignes",
        ]
        read_only_fields = [
            "numero_commande",
            "utilisateur",
            "utilisateur_nom",
            "statut",
            "total",
            "date_creation",
            "date_paiement",
            "reference_paiement",
        ]

    def get_utilisateur_nom(self, obj):
        u = obj.utilisateur
        full = f"{getattr(u, 'first_name', '')} {getattr(u, 'last_name', '')}".strip()
        return full if full else getattr(u, "email", str(u.id))


class CreateCommandeItemSerializer(serializers.Serializer):
    offre = serializers.IntegerField()
    quantite = serializers.IntegerField(min_value=1)


class CreateCommandeSerializer(serializers.Serializer):
    items = CreateCommandeItemSerializer(many=True)

    def validate_items(self, items):
        if not items:
            raise serializers.ValidationError("Le panier est vide.")
        return items