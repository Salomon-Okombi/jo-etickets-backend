from rest_framework import serializers
from .models import Paiement
from commandes.models import Commande


class PaiementSerializer(serializers.ModelSerializer):
    utilisateur_nom = serializers.SerializerMethodField()
    commande_numero = serializers.CharField(source="commande.numero_commande", read_only=True)

    class Meta:
        model = Paiement
        fields = [
            "id",
            "reference",
            "utilisateur",
            "utilisateur_nom",
            "commande",
            "commande_numero",
            "montant",
            "statut",
            "provider",
            "date_creation",
            "date_confirmation",
            "raw_payload",
        ]
        read_only_fields = [
            "id",
            "reference",
            "utilisateur",
            "utilisateur_nom",
            "statut",
            "date_creation",
            "date_confirmation",
        ]

    def get_utilisateur_nom(self, obj):
        u = obj.utilisateur
        full = f"{getattr(u, 'first_name', '')} {getattr(u, 'last_name', '')}".strip()
        return full if full else getattr(u, "email", str(u.id))


class CreatePaiementSerializer(serializers.Serializer):
    commande = serializers.IntegerField()
    provider = serializers.ChoiceField(choices=["MOCK", "STRIPE", "PAYPAL"], default="MOCK")
    raw_payload = serializers.JSONField(required=False)

    def validate_commande(self, commande_id):
        try:
            cmd = Commande.objects.get(id=commande_id)
        except Commande.DoesNotExist:
            raise serializers.ValidationError("Commande introuvable.")
        return cmd

    def validate(self, attrs):
        cmd: Commande = attrs["commande"]
        user = self.context["request"].user

        if not user.is_staff and cmd.utilisateur_id != user.id:
            raise serializers.ValidationError("Vous ne pouvez pas payer cette commande.")

        if cmd.statut != "EN_ATTENTE":
            raise serializers.ValidationError("Commande non payable.")

        return attrs


class ConfirmerPaiementSerializer(serializers.Serializer):
    success = serializers.BooleanField(default=True)
    reference_paiement = serializers.CharField(required=False, allow_blank=True)
    raw_payload = serializers.JSONField(required=False)