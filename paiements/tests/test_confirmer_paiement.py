import uuid
from base64 import b64decode
from decimal import Decimal
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APITestCase

from billets.models import EBillet
from commandes.models import Commande, LigneCommande
from evenements.models import Evenement
from offres.models import Offre, CategorieOffre
from paiements.models import Paiement


User = get_user_model()


class ConfirmPaiementAPITests(APITestCase):
    def setUp(self):
        now = timezone.now()

        self.user = User.objects.create_user(
            username="client_test",
            email="client@test.com",
            password="Test1234!",
            role="UTILISATEUR",
        )

        self.other_user = User.objects.create_user(
            username="other_user",
            email="other@test.com",
            password="Test1234!",
            role="UTILISATEUR",
        )

        self.event = Evenement.objects.create(
            nom_evenement="Finale Natation",
            discipline="Natation",
            lieu="Centre Aquatique",
            date_debut=now - timedelta(hours=2),
            date_fin=now + timedelta(days=1),
            statut="PUBLIE",
            prix_base=Decimal("15.00"),
            description_courte="Finale natation",
            description_longue="Grande finale natation",
        )

        code_duo = f"DUO_{uuid.uuid4().hex[:8].upper()}"

        self.categorie = CategorieOffre.objects.create(
            code=code_duo,
            nom="Offre Duo",
            description="2 personnes",
            nb_personnes=2,
            ordre_affichage=1,
            active=True,
            auto_apply_all_events=True,
        )

        self.offre = Offre.objects.create(
            evenement=self.event,
            categorie=self.categorie,
            createur=self.user,
            nom_offre="DUO - Finale Natation",
            description="Pack duo",
            quota_billets_total=20,
            quota_billets_restant=20,
            date_debut_vente=now - timedelta(days=1),
            date_fin_vente=now + timedelta(days=1),
            statut="ACTIVE",
        )

        self.commande = Commande.objects.create(
            utilisateur=self.user,
            statut="EN_ATTENTE",
            total=Decimal("60.00"),
        )

        # 2 packs DUO => 4 billets
        self.ligne = LigneCommande.objects.create(
            commande=self.commande,
            offre=self.offre,
            quantite=2,
            prix_unitaire=self.offre.prix,
            sous_total=(Decimal(str(self.offre.prix)) * Decimal("2")).quantize(Decimal("0.01")),
        )

        self.paiement = Paiement.objects.create(
            utilisateur=self.user,
            commande=self.commande,
            montant=self.commande.total,
            statut="INITIE",
            provider="MOCK",
        )

        self.confirm_url = f"/api/paiements/{self.paiement.id}/confirmer/"

    def test_confirmer_paiement_succes_paye_commande_et_genere_billets(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            self.confirm_url,
            {
                "success": True,
                "reference_paiement": "MOCK-CMD-001",
                "raw_payload": {"success": True, "provider": "MOCK"},
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)

        self.paiement.refresh_from_db()
        self.commande.refresh_from_db()
        self.offre.refresh_from_db()

        billets = EBillet.objects.filter(
            utilisateur=self.user,
            offre=self.offre,
        ).order_by("id")

        # paiement
        self.assertEqual(self.paiement.statut, "SUCCES")
        self.assertIsNotNone(self.paiement.date_confirmation)

        # commande
        self.assertEqual(self.commande.statut, "PAYEE")
        self.assertEqual(self.commande.reference_paiement, "MOCK-CMD-001")
        self.assertIsNotNone(self.commande.date_paiement)

        # quota : 2 packs DUO = 4 billets consommés
        self.assertEqual(self.offre.quota_billets_restant, 16)

        # billets générés
        self.assertEqual(billets.count(), 4)

        for billet in billets:
            self.assertEqual(billet.statut, "VALIDE")
            self.assertTrue(billet.cle_achat)
            self.assertTrue(billet.cle_finale)
            self.assertTrue(billet.qr_code)
            self.assertEqual(len(billet.cle_finale), 64)

            decoded_qr = b64decode(billet.qr_code)
            self.assertTrue(len(decoded_qr) > 0)

    def test_confirmer_paiement_deja_traite_refuse(self):
        self.client.force_authenticate(user=self.user)

        first = self.client.post(
            self.confirm_url,
            {
                "success": True,
                "reference_paiement": "MOCK-CMD-002",
            },
            format="json",
        )
        self.assertEqual(first.status_code, 200)

        second = self.client.post(
            self.confirm_url,
            {
                "success": True,
                "reference_paiement": "MOCK-CMD-003",
            },
            format="json",
        )
        self.assertEqual(second.status_code, 400)
        self.assertIn("detail", second.data)

        self.paiement.refresh_from_db()
        self.commande.refresh_from_db()
        self.offre.refresh_from_db()

        self.assertEqual(self.paiement.statut, "SUCCES")
        self.assertEqual(self.commande.statut, "PAYEE")

        self.assertEqual(
            EBillet.objects.filter(utilisateur=self.user, offre=self.offre).count(),
            4,
        )
        self.assertEqual(self.offre.quota_billets_restant, 16)

    def test_confirmer_paiement_en_echec_ne_genere_aucun_billet(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            self.confirm_url,
            {
                "success": False,
                "raw_payload": {"success": False},
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)

        self.paiement.refresh_from_db()
        self.commande.refresh_from_db()
        self.offre.refresh_from_db()

        self.assertEqual(self.paiement.statut, "ECHEC")
        self.assertIsNotNone(self.paiement.date_confirmation)

        self.assertEqual(self.commande.statut, "EN_ATTENTE")
        self.assertIsNone(self.commande.date_paiement)

        self.assertEqual(
            EBillet.objects.filter(utilisateur=self.user, offre=self.offre).count(),
            0,
        )
        self.assertEqual(self.offre.quota_billets_restant, 20)

    def test_confirmer_paiement_refuse_si_commande_plus_payable(self):
        self.client.force_authenticate(user=self.user)

        self.commande.statut = "ANNULEE"
        self.commande.save(update_fields=["statut"])

        response = self.client.post(
            self.confirm_url,
            {
                "success": True,
                "reference_paiement": "MOCK-CMD-004",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)

        self.paiement.refresh_from_db()
        self.commande.refresh_from_db()

        self.assertEqual(self.paiement.statut, "ANNULE")
        self.assertIsNotNone(self.paiement.date_confirmation)
        self.assertEqual(self.commande.statut, "ANNULEE")

        self.assertEqual(
            EBillet.objects.filter(utilisateur=self.user, offre=self.offre).count(),
            0,
        )

    def test_confirmer_paiement_refuse_pour_utilisateur_non_proprietaire(self):
        self.client.force_authenticate(user=self.other_user)

        response = self.client.post(
            self.confirm_url,
            {
                "success": True,
                "reference_paiement": "MOCK-CMD-005",
            },
            format="json",
        )

        self.assertIn(response.status_code, [403, 404])

        self.paiement.refresh_from_db()
        self.commande.refresh_from_db()

        self.assertEqual(self.paiement.statut, "INITIE")
        self.assertEqual(self.commande.statut, "EN_ATTENTE")
        self.assertEqual(
            EBillet.objects.filter(utilisateur=self.user, offre=self.offre).count(),
            0,
        )


class ConfirmPaiementModelLogicTests(TestCase):
    def setUp(self):
        now = timezone.now()

        self.user = User.objects.create_user(
            username="client_model",
            email="client_model@test.com",
            password="Test1234!",
            role="UTILISATEUR",
        )

        self.event = Evenement.objects.create(
            nom_evenement="Basket Finale",
            discipline="Basket",
            lieu="Arena Bercy",
            date_debut=now - timedelta(hours=1),
            date_fin=now + timedelta(days=1),
            statut="PUBLIE",
            prix_base=Decimal("20.00"),
            description_courte="Finale basket",
            description_longue="Grande finale basket",
        )

        code_solo = f"SOLO_{uuid.uuid4().hex[:8].upper()}"

        self.categorie = CategorieOffre.objects.create(
            code=code_solo,
            nom="Offre Solo",
            description="1 personne",
            nb_personnes=1,
            ordre_affichage=1,
            active=True,
            auto_apply_all_events=True,
        )

        self.offre = Offre.objects.create(
            evenement=self.event,
            categorie=self.categorie,
            createur=self.user,
            nom_offre="SOLO - Basket Finale",
            description="Pack solo",
            quota_billets_total=5,
            quota_billets_restant=5,
            date_debut_vente=now - timedelta(days=1),
            date_fin_vente=now + timedelta(days=1),
            statut="ACTIVE",
        )

        self.commande = Commande.objects.create(
            utilisateur=self.user,
            statut="EN_ATTENTE",
            total=Decimal("20.00"),
        )

        LigneCommande.objects.create(
            commande=self.commande,
            offre=self.offre,
            quantite=1,
            prix_unitaire=self.offre.prix,
            sous_total=Decimal(str(self.offre.prix)).quantize(Decimal("0.01")),
        )

    def test_creation_paiement_initie(self):
        paiement = Paiement.objects.create(
            utilisateur=self.user,
            commande=self.commande,
            montant=self.commande.total,
            statut="INITIE",
            provider="MOCK",
        )

        self.assertEqual(paiement.statut, "INITIE")
        self.assertEqual(paiement.montant, self.commande.total)
        self.assertEqual(paiement.commande_id, self.commande.id)
        self.assertTrue(paiement.reference)
