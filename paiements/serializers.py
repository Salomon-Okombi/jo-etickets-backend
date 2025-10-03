from rest_framework import serializers
from .models import Commande
from paniers.serializers import PanierSerializer

class CommandeSerializer(serializers.ModelSerializer):
    panier = PanierSerializer(read_only=True)

    class Meta:
        model = Commande
        fields = "__all__"
        read_only_fields = ["numero_commande", "date_commande", "montant_total", "utilisateur"]
