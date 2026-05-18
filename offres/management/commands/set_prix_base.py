from decimal import Decimal
from django.core.management.base import BaseCommand
from evenements.models import Evenement

class Command(BaseCommand):
    help = "Met un prix_base par défaut sur les événements dont prix_base=0.00"

    def add_arguments(self, parser):
        parser.add_argument("value", type=str, help="Ex: 10.00")

    def handle(self, *args, **options):
        val = Decimal(options["value"])
        updated = Evenement.objects.filter(prix_base=Decimal("0.00")).update(prix_base=val)
        self.stdout.write(self.style.SUCCESS(f"Evenements mis à jour (prix_base=0.00 -> {val}) : {updated}"))