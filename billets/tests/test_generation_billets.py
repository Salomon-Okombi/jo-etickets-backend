import uuid
from base64 import b64decode
from decimal import Decimal
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from billets.models import EBillet
from commandes.models import Commande, LigneCommande
from commandes.services import payer_commande_et_generer_billets
from evenements.models import Evenement
from offres.models import Offre, CategorieOffre


User = get_user_model()


class GenerationBilletsTests(TestCase):
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

        # prix recalculé dans Offre.save()
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

    def test_payer_commande_genere_billets_avec_cle_finale_et_qr_code(self):
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

            # champs sécurité présents
            self.assertTrue(billet.cle_achat)
            self.assertTrue(billet.cle_finale)
            self.assertTrue(billet.qr_code)

            # hmac sha256 hex => 64 caractères
            self.assertEqual(len(billet.cle_finale), 64)

            # la clé finale ne doit pas être identique à la clé d'achat
            self.assertNotEqual(billet.cle_finale, billet.cle_achat)

            # le QR base64 doit être décodable
            decoded = b64decode(billet.qr_code)
            self.assertTrue(len(decoded) > 0)

    def test_cles_finales_sont_uniques_pour_chaque_billet(self):
        payer_commande_et_generer_billets(
            self.commande,
            reference="MOCK-CMD-TEST-002",
        )

        billets = EBillet.objects.filter(
            utilisateur=self.user,
            offre=self.offre,
        )

        cles_finales = list(billets.values_list("cle_finale", flat=True))
        cles_achat = list(billets.values_list("cle_achat", flat=True))

        self.assertEqual(len(cles_finales), 4)
        self.assertEqual(len(cles_finales), len(set(cles_finales)))
        self.assertEqual(len(cles_achat), len(set(cles_achat)))

    def test_paiement_est_idempotent_et_ne_duplique_pas_les_billets(self):
        payer_commande_et_generer_billets(
            self.commande,
            reference="MOCK-CMD-TEST-003",
        )

        self.commande.refresh_from_db()
        self.offre.refresh_from_db()

        count_apres_premier_paiement = EBillet.objects.filter(
            utilisateur=self.user,
            offre=self.offre,
        ).count()
        quota_apres_premier_paiement = self.offre.quota_billets_restant

        # deuxième appel : ne doit rien regénérer
        payer_commande_et_generer_billets(
            self.commande,
            reference="MOCK-CMD-TEST-004",
        )

        self.commande.refresh_from_db()
        self.offre.refresh_from_db()

        count_apres_second_paiement = EBillet.objects.filter(
            utilisateur=self.user,
            offre=self.offre,
        ).count()
        quota_apres_second_paiement = self.offre.quota_billets_restant

        self.assertEqual(self.commande.statut, "PAYEE")
        self.assertEqual(count_apres_premier_paiement, 4)
        self.assertEqual(count_apres_second_paiement, 4)
        self.assertEqual(quota_apres_premier_paiement, 16)
        self.assertEqual(quota_apres_second_paiement, 16)

    def test_refuse_paiement_si_quota_insuffisant(self):
        # on rend le quota insuffisant : 2 packs DUO => 4 billets requis
        self.offre.quota_billets_restant = 2
        self.offre.save(update_fields=["quota_billets_restant"])

        with self.assertRaisesMessage(Exception, "Quota insuffisant"):
            payer_commande_et_generer_billets(
                self.commande,
                reference="MOCK-CMD-TEST-005",
            )

        self.commande.refresh_from_db()
        self.offre.refresh_from_db()

        self.assertEqual(self.commande.statut, "EN_ATTENTE")
        self.assertEqual(
            EBillet.objects.filter(utilisateur=self.user, offre=self.offre).count(),
            0,
        )
        self.assertEqual(self.offre.quota_billets_restant, 2)