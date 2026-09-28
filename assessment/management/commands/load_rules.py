import json

from django.conf import settings
from django.core.management.base import BaseCommand

from assessment.models import Rule


class Command(BaseCommand):
    help = "Load association rules produced by analysis/analyze_and_train.py into the database."

    def handle(self, *args, **options):
        if not settings.ML_RULES_PATH.exists():
            self.stderr.write(self.style.ERROR(
                f"No rules.json found at {settings.ML_RULES_PATH}. "
                "Run analysis/analyze_and_train.py first."
            ))
            return

        with open(settings.ML_RULES_PATH) as f:
            records = json.load(f)

        Rule.objects.all().delete()
        Rule.objects.bulk_create([
            Rule(
                antecedents=r["antecedents"],
                consequents=r["consequents"],
                support=r["support"],
                confidence=r["confidence"],
                lift=r["lift"],
            )
            for r in records
        ])

        self.stdout.write(self.style.SUCCESS(f"Loaded {len(records)} association rules."))
