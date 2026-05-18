from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from django.db import transaction

from offres.models import Offre

MAP_STATUT = {
    "DISPONIBLE": "ACTIVE",
    "INACTIVE": "INACTIVE",
    "EPUISEE": "EPUISEE",
    "EXPIREE": "EXPIREE",
}

class Command(BaseCommand):
    help = "Normalise les offres: statut (compat) + recalc prix + dates vendables"

    def add_arguments(self, parser):
        parser.add_argument("--fix-dates", action="store_true", help="Force date_debut_vente <= now <= date_fin_vente")
        parser.add_argument("--days", type=int, default=60)

    @transaction.atomic
    def handle(self, *args, **options):
        fix_dates = options["fix_dates"]
        days = int(options["days"])

        now = timezone.now()
        start = now - timedelta(minutes=5)
        end = now + timedelta(days=days)

        for o in Offre.objects.select_related("evenement", "categorie").all():
            old = str(o.statut).upper()
            if old in MAP_STATUT:
                o.statut = MAP_STATUT[old]

            if fix_dates:
                o.date_debut_vente = start
                o.date_fin_vente = end

            # recalcul prix via o.save() (si ton save recalcule le prix)
            o.save()

        self.stdout.write(self.style.SUCCESS("Offres normalisées."))