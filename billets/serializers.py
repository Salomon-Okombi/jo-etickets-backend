from rest_framework import serializers
from .models import EBillet

class EBilletSerializer(serializers.ModelSerializer):
    utilisateur_nom = serializers.SerializerMethodField()
    offre_nom = serializers.SerializerMethodField()

    class Meta:
        model = EBillet
        fields = [
            "id",
            "numero_billet",
            "utilisateur",
            "utilisateur_nom",
            "offre",
            "offre_nom",
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
            "utilisateur_nom",
            "offre_nom",
        ]

    def get_utilisateur_nom(self, obj):
        u = obj.utilisateur
        # adapte selon ton modèle Utilisateur
        full = f"{getattr(u, 'first_name', '')} {getattr(u, 'last_name', '')}".strip()
        return full if full else getattr(u, "email", str(u.id))

    def get_offre_nom(self, obj):
        o = obj.offre
        return getattr(o, "nom", str(o.id))