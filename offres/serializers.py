from rest_framework import serializers
from .models import Offre


class OffreSerializer(serializers.ModelSerializer):
    evenement_nom = serializers.CharField(source="evenement.nom_evenement", read_only=True)

    # Champs catégorie lisibles côté frontend
    categorie_code = serializers.CharField(source="categorie.code", read_only=True)
    categorie_nom = serializers.CharField(source="categorie.nom", read_only=True)

    # Compat frontend : type_offre + nb_personnes
    type_offre = serializers.CharField(source="categorie.code", read_only=True)
    nb_personnes = serializers.IntegerField(source="categorie.nb_personnes", read_only=True)

    class Meta:
        model = Offre
        fields = [
            "id",
            "evenement",
            "evenement_nom",
            "categorie",
            "categorie_code",
            "categorie_nom",
            "nom_offre",
            "description",
            "prix",
            "type_offre",
            "nb_personnes",
            "stock_total",
            "stock_disponible",
            "date_debut_vente",
            "date_fin_vente",
            "statut",
            "createur",
            "date_creation",
            "date_modification",
        ]
        read_only_fields = ["createur", "date_creation", "date_modification", "evenement_nom", "categorie_code", "categorie_nom", "type_offre", "nb_personnes"]