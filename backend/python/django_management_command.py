# management/commands/deactivate_stale_users.py
#
# Django management command that bulk-deactivates user accounts which have
# not logged in for a configurable number of days. Processes records in
# batches to avoid loading the entire queryset into memory and reports
# progress to stdout as it goes.

import sys
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

User = get_user_model()


class Command(BaseCommand):
    help = "Deactivate user accounts inactive for a given number of days."

    def add_arguments(self, parser):
        parser.add_argument(
            "--days",
            type=int,
            default=90,
            help="Deactivate users whose last_login is older than this many days (default: 90).",
        )
        parser.add_argument(
            "--batch-size",
            type=int,
            default=500,
            help="Number of records to update per batch (default: 500).",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show how many users would be deactivated without making changes.",
        )

    def handle(self, *args, **options):
        days = options["days"]
        batch_size = options["batch_size"]
        dry_run = options["dry_run"]

        if days <= 0:
            raise CommandError("--days must be a positive integer.")
        if batch_size <= 0:
            raise CommandError("--batch-size must be a positive integer.")

        cutoff = timezone.now() - timedelta(days=days)
        queryset = User.objects.filter(is_active=True, last_login__lt=cutoff)
        total = queryset.count()

        if total == 0:
            self.stdout.write(self.style.SUCCESS("No stale users found. Nothing to do."))
            return

        self.stdout.write(f"Found {total} stale user(s) (inactive since before {cutoff:%Y-%m-%d}).")

        if dry_run:
            self.stdout.write(self.style.WARNING("Dry run enabled — no records will be modified."))
            return

        processed = 0
        # Use .iterator() to stream primary keys instead of caching the whole queryset.
        pk_iterator = queryset.order_by("pk").values_list("pk", flat=True).iterator(chunk_size=batch_size)

        batch = []
        for pk in pk_iterator:
            batch.append(pk)
            if len(batch) >= batch_size:
                processed += self._deactivate_batch(batch)
                self._report_progress(processed, total)
                batch = []

        if batch:
            processed += self._deactivate_batch(batch)
            self._report_progress(processed, total)

        self.stdout.write(self.style.SUCCESS(f"\nDeactivated {processed} user(s)."))

    def _deactivate_batch(self, pks):
        return User.objects.filter(pk__in=pks).update(is_active=False)

    def _report_progress(
