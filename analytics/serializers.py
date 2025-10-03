from rest_framework import serializers
from .models import StatistiquesVente

class StatistiquesVenteSerializer(serializers.ModelSerializer):
    offre_nom = serializers.CharField(source="offre.nom_offre", read_only=True)

    class Meta:
        model = StatistiquesVente
        fields = [
            "id",
            "offre",
            "offre_nom",
            "nombre_ventes",
            "chiffre_affaires",
            "date_derniere_maj",
            "moyenne_ventes_jour",
            "pic_ventes_heure",
        ]
        read_only_fields = ["date_derniere_maj"]
