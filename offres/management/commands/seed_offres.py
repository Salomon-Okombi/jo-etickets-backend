from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta

from offres.models import Offre, CategorieOffre
from evenements.models import Evenement
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = "Crée les offres manquantes pour tous les événements (Evenement × CategorieOffre active)."

    def add_arguments(self, parser):
        parser.add_argument("--stock", type=int, default=100)
        parser.add_argument("--days", type=int, default=60)
        parser.add_argument("--creator-id", type=int, default=None)

    def handle(self, *args, **options):
        stock = int(options["stock"])
        days = int(options["days"])
        creator_id = options.get("creator_id")

        User = get_user_model()
        createur = User.objects.filter(id=creator_id).first() if creator_id else None
        if not createur:
            createur = User.objects.filter(is_superuser=True).order_by("id").first()

        if not createur:
            self.stderr.write("Aucun createur trouvé. Crée un superuser ou passe --creator-id.")
            return

        start = timezone.now() - timedelta(minutes=5)
        end = timezone.now() + timedelta(days=days)

        cats = CategorieOffre.objects.filter(active=True).order_by("ordre_affichage", "nom")
        events = Evenement.objects.all()

        created_count = 0
        skipped_count = 0

        for ev in events:
            for cat in cats:
                obj, created = Offre.objects.get_or_create(
                    evenement=ev,
                    categorie=cat,
                    defaults={
                        "createur": createur,
                        "nom_offre": f"{cat.code} - {ev.nom_evenement}",
                        "description": cat.description or "",
                        "stock_total": stock,
                        "stock_disponible": stock,
                        "date_debut_vente": start,
                        "date_fin_vente": end,
                        "statut": "ACTIVE",
                    },
                )
                if created:
                    created_count += 1
                else:
                    skipped_count += 1

        self.stdout.write(self.style.SUCCESS(f"Offres créées : {created_count}"))
        self.stdout.write(self.style.SUCCESS(f"Offres déjà existantes : {skipped_count}"))
