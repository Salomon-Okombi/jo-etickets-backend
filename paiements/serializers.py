# paiements/serializers.py
from rest_framework import serializers
from django.db.models import Q
from paiements.models import Commande
from paniers.models import Panier, LignePanier


class LignePanierBriefSerializer(serializers.ModelSerializer):
    """Version compacte d'une ligne de panier pour exposer dans la commande."""
    offre_nom = serializers.CharField(source="offre.nom_offre", read_only=True)
    offre_prix = serializers.DecimalField(source="offre.prix", max_digits=8, decimal_places=2, read_only=True)

    class Meta:
        model = LignePanier
        fields = ["id", "offre", "offre_nom", "offre_prix", "quantite", "prix_unitaire", "sous_total", "date_ajout"]
        read_only_fields = ["id", "offre_nom", "offre_prix", "prix_unitaire", "sous_total", "date_ajout"]


class PanierBriefSerializer(serializers.ModelSerializer):
    """Panier compact intégré dans la représentation d'une commande."""
    lignes = LignePanierBriefSerializer(many=True, read_only=True)

    class Meta:
        model = Panier
        fields = ["id", "statut", "montant_total", "lignes", "date_creation", "date_expiration"]
        read_only_fields = ["id", "statut", "montant_total", "lignes", "date_creation", "date_expiration"]


class CommandeSerializer(serializers.ModelSerializer):
    # Exposer le panier en lecture de façon utile
    panier_detail = PanierBriefSerializer(source="panier", read_only=True)

    class Meta:
        model = Commande
        fields = [
            "id",
            "utilisateur",
            "panier",
            "panier_detail",          # 👈 ajout pratique en lecture
            "numero_commande",
            "date_commande",
            "montant_total",
            "statut_paiement",
            "methode_paiement",
            "reference_paiement",
            "date_paiement",
        ]
        # 🔒 Tout ce qui touche au paiement reste non éditable ici (réservé à l’endpoint /payer)
        read_only_fields = [
            "utilisateur",
            "numero_commande",
            "date_commande",
            "montant_total",
            "statut_paiement",
            "methode_paiement",
            "reference_paiement",
            "date_paiement",
            "panier_detail",
        ]

    # --------------------------
    # Validations renforcées
    # --------------------------
    def validate_panier(self, panier: Panier):
        """
        - Le panier ne doit pas être vide
        - Le panier doit appartenir à l'utilisateur courant
        - Le panier ne doit pas déjà être associé à une commande
        - Toutes les lignes doivent référencer une 'offre' non nulle
        """
        # 1) non vide
        if not panier.lignes.exists():
            raise serializers.ValidationError("Le panier est vide, impossible de créer une commande.")

        # 2) propriétaire
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            if panier.utilisateur_id != request.user.id and not request.user.is_staff:
                raise serializers.ValidationError("Ce panier n'appartient pas à l'utilisateur connecté.")
        # si pas de request (tests unitaires), on laisse passer

        # 3) déjà commandé ?
        if hasattr(panier, "commande") and panier.commande is not None:
            raise serializers.ValidationError("Ce panier est déjà associé à une commande.")

        # 4) lignes valides (offre non nulle)
        if panier.lignes.filter(offre__isnull=True).exists():
            raise serializers.ValidationError(
                "Le panier contient des lignes invalides (offre manquante). Veuillez corriger le panier."
            )

        return panier

    def validate(self, attrs):
        """
        Validation globale : protection supplémentaire si besoin.
        - Ex : empêcher la création si statut du panier est 'ABANDONNE' ou 'EXPIRE'
        """
        panier: Panier = attrs.get("panier")
        if panier and panier.statut in {"ABANDONNE", "EXPIRE"}:
            raise serializers.ValidationError("Impossible de créer une commande à partir d’un panier abandonné ou expiré.")
        return attrs
