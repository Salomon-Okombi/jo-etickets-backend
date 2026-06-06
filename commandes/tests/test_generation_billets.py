# Last edited by you@example.com @ 06/06/26 19:56.
import uuid
from base64 import b64decode
from decimal import Decimal
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from billets.models import EBillet
from commandes.models import Commande, LigneCommande
from commandes.services import payer_commande_et_generer_billets
from evenements.models import Evenement
from offres.models import Offre, CategorieOffre


User = get_user_model()


class TestGenerationBillets(TestCase):
    def setUp(self):
        now = timezone.now()

        self.user = User.objects.create_user(
            username="client_test",
            email="client@test.com",
            password="Test1234!",
            role="UTILISATEUR",
        )

        self.event = Evenement.objects.create(
            nom_evenement="Finale 100m",
            discipline="Athlétisme",
            lieu="Stade de France",
            date_debut=now - timedelta(hours=2),
            date_fin=now + timedelta(days=1),
            statut="PUBLIE",
            prix_base=Decimal("12.00"),
            description_courte="Finale 100m",
            description_longue="Grande finale du 100m",
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
            nom_offre="DUO - Finale 100m",
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
            total=Decimal("48.00"),
        )

        self.ligne = LigneCommande.objects.create(
            commande=self.commande,
            offre=self.offre,
            quantite=2,  # 2 packs DUO => 4 billets
            prix_unitaire=self.offre.prix,
            sous_total=(Decimal(str(self.offre.prix)) * Decimal("2")).quantize(Decimal("0.01")),
        )

    def test_payer_commande_genere_le_bon_nombre_de_billets(self):
        payer_commande_et_generer_billets(
            self.commande,
            reference="MOCK-CMD-TEST-001",
        )

        self.commande.refresh_from_db()
        self.offre.refresh_from_db()

        billets = EBillet.objects.filter(
            utilisateur=self.user,
            offre=self.offre,
        ).order_by("id")

        # 2 packs DUO => 4 billets
        self.assertEqual(billets.count(), 4)

        # commande payée
        self.assertEqual(self.commande.statut, "PAYEE")
        self.assertEqual(self.commande.reference_paiement, "MOCK-CMD-TEST-001")
        self.assertIsNotNone(self.commande.date_paiement)

        # quota décrémenté de 4 billets
        self.assertEqual(self.offre.quota_billets_restant, 16)

        for billet in billets:
            self.assertEqual(billet.statut, "VALIDE")
            self.assertEqual(billet.prix_paye, self.ligne.prix_unitaire)

    def test_billets_generes_avec_cle_achat_cle_finale_et_qr_code(self):
        payer_commande_et_generer_billets(
            self.commande,
            reference="MOCK-CMD-TEST-002",
        )

        billets = EBillet.objects.filter(
            utilisateur=self.user,
            offre=self.offre,
        ).order_by("id")

        self.assertEqual(billets.count(), 4)

        for billet in billets:
            self.assertTrue(billet.cle_achat)
            self.assertTrue(billet.cle_finale)
            self.assertTrue(billet.qr_code)

            # cle_finale HMAC SHA256 hex => 64 caractères
            self.assertEqual(len(billet.cle_finale), 64)

            # les deux clés doivent être différentes
            self.assertNotEqual(billet.cle_achat, billet.cle_finale)

            # le qr_code base64 doit être décodable
            decoded_png = b64decode(billet.qr_code)
            self.assertTrue(len(decoded_png) > 0)

    def test_cles_achat_et_cles_finales_sont_uniques(self):
        payer_commande_et_generer_billets(
            self.commande,
            reference="MOCK-CMD-TEST-003",
        )

        billets = EBillet.objects.filter(
            utilisateur=self.user,
            offre=self.offre,
        )

        cles_achat = list(billets.values_list("cle_achat", flat=True))
        cles_finales = list(billets.values_list("cle_finale", flat=True))

        self.assertEqual(len(cles_achat), 4)
        self.assertEqual(len(cles_finales), 4)
        self.assertEqual(len(set(cles_achat)), 4)
        self.assertEqual(len(set(cles_finales)), 4)

    def test_paiement_est_idempotent_et_ne_duplique_pas_les_billets(self):
        payer_commande_et_generer_billets(
            self.commande,
            reference="MOCK-CMD-TEST-004",
        )

        self.commande.refresh_from_db()
        self.offre.refresh_from_db()

        count_1 = EBillet.objects.filter(
            utilisateur=self.user,
            offre=self.offre,
        ).count()
        quota_1 = self.offre.quota_billets_restant

        # second appel : ne doit rien refaire
        payer_commande_et_generer_billets(
            self.commande,
            reference="MOCK-CMD-TEST-005",
        )

        self.commande.refresh_from_db()
        self.offre.refresh_from_db()

        count_2 = EBillet.objects.filter(
            utilisateur=self.user,
            offre=self.offre,
        ).count()
        quota_2 = self.offre.quota_billets_restant

        self.assertEqual(self.commande.statut, "PAYEE")
        self.assertEqual(count_1, 4)
        self.assertEqual(count_2, 4)
        self.assertEqual(quota_1, 16)
        self.assertEqual(quota_2, 16)

    def test_refuse_paiement_si_quota_insuffisant(self):
        # 2 packs DUO => 4 billets requis
        self.offre.quota_billets_restant = 2
        self.offre.save(update_fields=["quota_billets_restant"])

        with self.assertRaises(ValidationError) as ctx:
            payer_commande_et_generer_billets(
                self.commande,
                reference="MOCK-CMD-TEST-006",
            )

        self.assertIn("Quota insuffisant", str(ctx.exception))

        self.commande.refresh_from_db()
        self.offre.refresh_from_db()

        self.assertEqual(self.commande.statut, "EN_ATTENTE")
        self.assertEqual(self.offre.quota_billets_restant, 2)
        self.assertEqual(
            EBillet.objects.filter(utilisateur=self.user, offre=self.offre).count(),
            0,
        )

    def test_refuse_paiement_si_commande_non_payable(self):
        self.commande.statut = "ANNULEE"
        self.commande.save(update_fields=["statut"])

        with self.assertRaises(ValidationError) as ctx:
            payer_commande_et_generer_billets(
                self.commande,
                reference="MOCK-CMD-TEST-007",
            )

        self.assertIn("Commande non payable", str(ctx.exception))

        self.assertEqual(
            EBillet.objects.filter(utilisateur=self.user, offre=self.offre).count(),
            0,
        )

    def test_refuse_paiement_si_commande_vide(self):
        self.ligne.delete()

        with self.assertRaises(ValidationError) as ctx:
            payer_commande_et_generer_billets(
                self.commande,
                reference="MOCK-CMD-TEST-008",
            )

        self.assertIn("Commande vide", str(ctx.exception))

        self.assertEqual(
            EBillet.objects.filter(utilisateur=self.user, offre=self.offre).count(),
            0,
        )