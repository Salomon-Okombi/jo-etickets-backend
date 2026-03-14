from rest_framework.test import APITestCase
from django.urls import reverse
from django.utils import timezone
from decimal import Decimal

from users.models import Utilisateur
from offres.models import Offre
from evenements.models import Evenement
from commandes.models import Commande, LigneCommande
from paiements.models import Paiement


class PaiementsAPITest(APITestCase):
    def setUp(self):
        self.user = Utilisateur.objects.create_user(email="u@test.com", password="Test12345!")
        self.client.force_authenticate(user=self.user)

        self.event = Evenement.objects.create(
            nom="Test Event",
            discipline_sportive="Test",
            date_evenement=timezone.now().date(),
            lieu_evenement="Paris",
            description="x",
            statut="A_VENIR",
        )

        self.offre = Offre.objects.create(
            evenement=self.event,
            createur=self.user,
            nom_offre="SOLO",
            description="x",
            prix=Decimal("10.00"),
            nb_personnes=1,
            type_offre="SOLO",
            stock_total=10,
            stock_disponible=10,
            date_debut_vente=timezone.now(),
            date_fin_vente=timezone.now(),
            statut="ACTIVE",
            lieu_evenement="Paris",
            discipline_sportive="Test",
        )

        self.cmd = Commande.objects.create(utilisateur=self.user, statut="EN_ATTENTE", total=Decimal("10.00"))
        LigneCommande.objects.create(
            commande=self.cmd,
            offre=self.offre,
            quantite=1,
            prix_unitaire=Decimal("10.00"),
            sous_total=Decimal("10.00"),
        )

    def test_create_paiement(self):
        url = "/api/paiements/"
        res = self.client.post(url, {"commande": self.cmd.id, "provider": "MOCK"}, format="json")
        self.assertEqual(res.status_code, 201)
        self.assertEqual(res.data["statut"], "INITIE")

    def test_confirm_paiement_success(self):
        p = Paiement.objects.create(utilisateur=self.user, commande=self.cmd, montant=self.cmd.total, provider="MOCK")
        url = f"/api/paiements/{p.id}/confirmer/"
        res = self.client.post(url, {"success": True}, format="json")
        self.assertEqual(res.status_code, 200)
        p.refresh_from_db()
        self.assertEqual(p.statut, "SUCCES")

    def test_confirm_paiement_fail(self):
        p = Paiement.objects.create(utilisateur=self.user, commande=self.cmd, montant=self.cmd.total, provider="MOCK")
        url = f"/api/paiements/{p.id}/confirmer/"
        res = self.client.post(url, {"success": False}, format="json")
        self.assertEqual(res.status_code, 400)
        p.refresh_from_db()
        self.assertEqual(p.statut, "ECHEC")