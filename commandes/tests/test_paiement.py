import pytest
from decimal import Decimal
from django.utils import timezone
from django.contrib.auth import get_user_model
import uuid

from evenements.models import Evenement
from offres.models import CategorieOffre, Offre
from billets.models import EBillet

from commandes.services import create_commande_from_items, payer_commande_et_generer_billets


pytestmark = pytest.mark.django_db


def _uniq(s: str) -> str:
    """Ajoute un suffixe unique pour éviter les collisions (code unique en DB)."""
    return f"{s}_{uuid.uuid4().hex[:8].upper()}"


def _make_user(email="user@test.com", password="Passw0rd!123", is_staff=False):
    User = get_user_model()

    fields = {f.name for f in User._meta.fields}
    kwargs = {"email": email, "is_staff": is_staff}

    # Beaucoup de custom user exigent username -> on le fournit si besoin
    if "username" in fields:
        kwargs["username"] = email.split("@")[0]

    # Certains modèles ont is_superuser requis en admin -> optionnel
    if is_staff and "is_superuser" in fields:
        kwargs["is_superuser"] = True

    return User.objects.create_user(**kwargs, password=password)


def _make_evenement(
    nom="Basket",
    prix_base=Decimal("5.00"),
    statut="PUBLIE",
):
    now = timezone.now()

    # IMPORTANT : adapte si ton modèle Evenement exige d'autres champs obligatoires
    ev = Evenement.objects.create(
        nom_evenement=_uniq(nom),
        prix_base=prix_base,
        statut=statut,
        date_debut=now - timezone.timedelta(days=1),
        date_fin=now + timezone.timedelta(days=30),
        # exemple si nécessaires :
        # lieu="Paris",
        # discipline="Basket",
    )
    return ev


def _make_categorie(code="DUO", nom="Duo", nb_personnes=2, active=True):
    # code unique pour éviter Duplicate entry (code est unique=True)
    unique_code = _uniq(code)

    cat = CategorieOffre.objects.create(
        code=unique_code,
        nom=nom,
        nb_personnes=nb_personnes,
        active=active,
        auto_apply_all_events=False,  # IMPORTANT : ne pas auto-créer des offres partout
        ordre_affichage=0,
    )
    return cat


def _make_offre(
    ev: Evenement,
    cat: CategorieOffre,
    createur,
    quota_total=10,
    quota_restant=10,
    statut="ACTIVE",
):
    now = timezone.now()

    offre = Offre.objects.create(
        evenement=ev,
        categorie=cat,
        createur=createur,
        nom_offre=f"{cat.code} - {ev.nom_evenement}",
        description="Offre test",
        quota_billets_total=quota_total,
        quota_billets_restant=quota_restant,
        date_debut_vente=now - timezone.timedelta(days=1),
        date_fin_vente=now + timezone.timedelta(days=10),
        statut=statut,
        # prix recalculé dans Offre.save() chez toi
        prix=Decimal("0.00"),
    )
    offre.refresh_from_db()
    return offre


def test_paiement_decremente_quota_et_genere_billets():
    """
    Fonctionnalité essentielle :
    - création commande EN_ATTENTE
    - paiement mock => PAYEE
    - décrément quota billets restant (packs * nb_personnes)
    - génération EBillets (packs * nb_personnes)
    - qr_code généré (base64 non vide)
    """
    user = _make_user(email=f"client_{uuid.uuid4().hex[:6]}@test.com", is_staff=False)
    admin = _make_user(email=f"admin_{uuid.uuid4().hex[:6]}@test.com", is_staff=True)

    ev = _make_evenement(nom="Volley", prix_base=Decimal("10.00"), statut="PUBLIE")
    cat = _make_categorie(code="DUO", nom="Duo", nb_personnes=2, active=True)
    offre = _make_offre(ev, cat, createur=admin, quota_total=10, quota_restant=10, statut="ACTIVE")

    # 2 packs DUO => 4 billets
    items = [{"offre": offre.id, "quantite": 2}]

    cmd = create_commande_from_items(user, items)
    cmd.refresh_from_db()
    assert cmd.statut == "EN_ATTENTE"
    assert cmd.lignes.count() == 1

    cmd = payer_commande_et_generer_billets(cmd, reference="MOCK-TEST-001")
    cmd.refresh_from_db()
    offre.refresh_from_db()

    # 1) commande payée
    assert cmd.statut == "PAYEE"
    assert cmd.reference_paiement == "MOCK-TEST-001"
    assert cmd.date_paiement is not None

    # 2) quota décrémenté : 10 - (2 packs * 2 personnes) = 6
    assert offre.quota_billets_restant == 6

    # 3) billets générés : 4
    billets = EBillet.objects.filter(utilisateur=user, offre=offre)
    assert billets.count() == 4

    # 4) QR code non vide (base64) sur chaque billet
    for b in billets:
        assert b.qr_code is not None
        assert isinstance(b.qr_code, str)
        assert len(b.qr_code) > 50


def test_paiement_idempotent_ne_cree_pas_de_billets_en_double():
    """
    Bonus : idempotence
    - payer deux fois ne doit pas doubler les billets ni re-décrémenter le quota.
    """
    user = _make_user(email=f"client_{uuid.uuid4().hex[:6]}@test.com", is_staff=False)
    admin = _make_user(email=f"admin_{uuid.uuid4().hex[:6]}@test.com", is_staff=True)

    ev = _make_evenement(nom="Basket", prix_base=Decimal("7.00"), statut="PUBLIE")
    cat = _make_categorie(code="SOLO", nom="Solo", nb_personnes=1, active=True)
    offre = _make_offre(ev, cat, createur=admin, quota_total=5, quota_restant=5, statut="ACTIVE")

    # 3 packs SOLO => 3 billets
    items = [{"offre": offre.id, "quantite": 3}]

    cmd = create_commande_from_items(user, items)
    cmd = payer_commande_et_generer_billets(cmd, reference="MOCK-TEST-002")

    offre.refresh_from_db()
    assert EBillet.objects.filter(utilisateur=user, offre=offre).count() == 3
    assert offre.quota_billets_restant == 2  # 5 - 3

    # Appel 2 : ne doit rien changer
    cmd2 = payer_commande_et_generer_billets(cmd, reference="MOCK-TEST-002-RETRY")
    offre.refresh_from_db()

    assert cmd2.statut == "PAYEE"
    assert EBillet.objects.filter(utilisateur=user, offre=offre).count() == 3
    assert offre.quota_billets_restant == 2