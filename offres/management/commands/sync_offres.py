# offres/management/commands/sync_offres.py
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from evenements.models import Evenement
from offres.models import CategorieOffre, Offre


DEFAULT_QUOTA_BILLETS = 100
DEFAULT_DAYS = 60


class Command(BaseCommand):
    help = (
        "Synchronise les offres (evenement × categorie) pour toutes les catégories globales actives. "
        "Crée les offres manquantes et peut optionnellement mettre à jour les offres existantes."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--quota",
            type=int,
            default=DEFAULT_QUOTA_BILLETS,
            help="Quota de billets par défaut (places) à appliquer aux offres créées (default: 100).",
        )
        parser.add_argument(
            "--days",
            type=int,
            default=DEFAULT_DAYS,
            help="Durée en jours pour date_fin_vente par défaut (default: 60).",
        )
        parser.add_argument(
            "--include-expired-events",
            action="store_true",
            help="Inclure aussi les événements expirés (par défaut: seulement non expirés).",
        )
        parser.add_argument(
            "--update-existing",
            action="store_true",
            help="Mettre à jour les offres déjà existantes (nom, description, dates, quota si besoin).",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Simulation : n'écrit rien en base, affiche seulement ce qui serait fait.",
        )

    def handle(self, *args, **options):
        quota_default: int = options["quota"]
        days: int = options["days"]
        include_expired: bool = options["include_expired_events"]
        update_existing: bool = options["update_existing"]
        dry_run: bool = options["dry_run"]

        now = timezone.now()
        start_default = now - timedelta(minutes=5)
        end_default = now + timedelta(days=days)

        # Catégories globales actives uniquement
        categories = (
            CategorieOffre.objects
            .filter(active=True, auto_apply_all_events=True)
            .order_by("ordre_affichage", "nom")
        )

        if include_expired:
            events = Evenement.objects.all().order_by("date_debut")
        else:
            events = Evenement.objects.filter(date_fin__gte=now).order_by("date_debut")

        cat_count = categories.count()
        ev_count = events.count()

        self.stdout.write(self.style.MIGRATE_HEADING("SYNC OFFRES"))
        self.stdout.write(f"- Catégories globales actives: {cat_count}")
        self.stdout.write(f"- Événements ciblés: {ev_count}")
        self.stdout.write(f"- Quota billets par défaut: {quota_default}")
        self.stdout.write(f"- Fenêtre de vente par défaut: start={start_default.isoformat()} end={end_default.isoformat()}")
        self.stdout.write(f"- Update existing: {update_existing}")
        self.stdout.write(f"- Dry run: {dry_run}")

        created = 0
        updated = 0
        skipped = 0

        # Tout dans une transaction si on n'est pas en dry-run
        ctx = transaction.atomic() if not dry_run else _nullcontext()

        with ctx:
            for ev in events:
                # fin de vente ne dépasse pas la fin de l'événement
                end = end_default
                if getattr(ev, "date_fin", None):
                    end = min(end_default, ev.date_fin)

                for cat in categories:
                    defaults = {
                        "createur": self._pick_creator(),
                        "nom_offre": f"{cat.code} - {ev.nom_evenement}",
                        "description": cat.description or "",
                        "quota_billets_total": quota_default,
                        "quota_billets_restant": quota_default,
                        "date_debut_vente": start_default,
                        "date_fin_vente": end,
                        "statut": "ACTIVE",
                    }

                    # get_or_create nécessite createur obligatoire :
                    # - si ton champ createur n'accepte pas null, il faut une stratégie.
                    # Ici, on impose un créateur via -- (voir _pick_creator)
                    obj, was_created = Offre.objects.get_or_create(
                        evenement=ev,
                        categorie=cat,
                        defaults=defaults,
                    )

                    if was_created:
                        created += 1
                        if dry_run:
                            self.stdout.write(f"[DRY] CREATE Offre(ev={ev.id}, cat={cat.code})")
                        continue

                    if not update_existing:
                        skipped += 1
                        continue

                    # Mise à jour contrôlée des champs (sans casser quota restant déjà consommé)
                    changed = False

                    # Nom/description
                    new_nom = f"{cat.code} - {ev.nom_evenement}"
                    if obj.nom_offre != new_nom:
                        obj.nom_offre = new_nom
                        changed = True

                    new_desc = cat.description or ""
                    if (obj.description or "") != new_desc:
                        obj.description = new_desc
                        changed = True

                    # Fenêtre vente (on resserre si événement plus tôt)
                    if obj.date_debut_vente != start_default:
                        obj.date_debut_vente = start_default
                        changed = True
                    if obj.date_fin_vente != end:
                        obj.date_fin_vente = end
                        changed = True

                    # Quota total : si tu veux imposer un quota par défaut
                    # Attention : on ne doit pas remonter quota_restant au-dessus de quota_total
                    if obj.quota_billets_total != quota_default:
                        obj.quota_billets_total = quota_default
                        if obj.quota_billets_restant > quota_default:
                            obj.quota_billets_restant = quota_default
                        changed = True

                    # Statut : on ne force pas si tu as volontairement mis INACTIVE, sauf si tu veux
                    # Ici: on ne force pas.

                    if changed:
                        updated += 1
                        if dry_run:
                            self.stdout.write(f"[DRY] UPDATE Offre(ev={ev.id}, cat={cat.code})")
                        else:
                            obj.save()
                    else:
                        skipped += 1

            if dry_run:
                # En dry-run on annule tout
                raise _DryRunRollback()

        self.stdout.write(self.style.SUCCESS("Terminé."))
        self.stdout.write(f"Créées: {created}")
        self.stdout.write(f"Mises à jour: {updated}")
        self.stdout.write(f"Inchangées: {skipped}")

    def _pick_creator(self):
        """
        Offre.createur est obligatoire.
        Stratégie minimale :
        - si tu as un superuser/staff "system" dédié, tu peux le récupérer ici.
        - sinon, on peut mettre le premier staff/superuser.

        IMPORTANT :
        - Tu dois adapter ce choix à ton projet (ex: user 'admin').
        """
        from django.contrib.auth import get_user_model
        User = get_user_model()

        # Choix simple : premier superuser, sinon premier staff
        u = User.objects.filter(is_superuser=True).order_by("id").first()
        if u:
            return u
        u = User.objects.filter(is_staff=True).order_by("id").first()
        if u:
            return u

        # Si aucun user staff/superuser, on ne peut pas créer d'offre
        # car createur est PROTECT et non-nullable.
        raise RuntimeError(
            "Impossible de synchroniser : aucun utilisateur staff/superuser trouvé pour renseigner Offre.createur."
        )


class _DryRunRollback(Exception):
    """Exception interne pour annuler la transaction en mode dry-run."""
    pass


class _nullcontext:
    """Context manager minimal quand on ne veut pas de transaction."""
    def __enter__(self):
        return None

    def __exit__(self, exc_type, exc, tb):
        return False