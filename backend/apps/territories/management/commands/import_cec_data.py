"""
Management command to import CEC electoral territory data.

Accepts a JSON or CSV file and creates/updates the Region → District → Precinct hierarchy.
Idempotent: re-running will update existing records without creating duplicates.

JSON format expected:
[
  {
    "region_name": "Tbilisi",
    "region_name_ka": "თბილისი",
    "region_code": "TB",
    "district_name": "Didube-Chughureti",
    "district_name_ka": "დიდუბე-ჩუღურეთი",
    "district_cec_code": "01.01",
    "precinct_name": "Precinct 1",
    "precinct_name_ka": "საარჩევნო უბანი 1",
    "precinct_cec_code": "01.01.001",
    "latitude": 41.7151,
    "longitude": 44.8271
  },
  ...
]

CSV format expected (same field names as column headers).
"""

import csv
import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.territories.models import District, Precinct, Region


class Command(BaseCommand):
    help = "Import CEC electoral data from a JSON or CSV file into the territory hierarchy."

    def add_arguments(self, parser):
        parser.add_argument(
            "file_path",
            type=str,
            help="Path to the JSON or CSV file containing CEC territory data.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Parse and validate the file without writing to the database.",
        )

    def handle(self, *args, **options):
        file_path = Path(options["file_path"])
        dry_run = options["dry_run"]

        if not file_path.exists():
            raise CommandError(f"File not found: {file_path}")

        suffix = file_path.suffix.lower()
        if suffix == ".json":
            rows = self._load_json(file_path)
        elif suffix == ".csv":
            rows = self._load_csv(file_path)
        else:
            raise CommandError("Unsupported file format. Use .json or .csv")

        self.stdout.write(f"Loaded {len(rows)} rows from {file_path.name}")

        if dry_run:
            self.stdout.write(self.style.WARNING("Dry run — no changes written."))
            self._validate_rows(rows)
            return

        counters = {"regions": 0, "districts": 0, "precincts": 0}
        with transaction.atomic():
            for row in rows:
                self._process_row(row, counters)

        self.stdout.write(
            self.style.SUCCESS(
                f"Done. Regions: {counters['regions']} created/updated, "
                f"Districts: {counters['districts']} created/updated, "
                f"Precincts: {counters['precincts']} created/updated."
            )
        )

    # ------------------------------------------------------------------
    # Loaders
    # ------------------------------------------------------------------

    def _load_json(self, path):
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, list):
            raise CommandError("JSON file must contain a top-level array of objects.")
        return data

    def _load_csv(self, path):
        with open(path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            return list(reader)

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    REQUIRED_FIELDS = {
        "region_name",
        "region_name_ka",
        "region_code",
        "district_name",
        "district_name_ka",
        "district_cec_code",
        "precinct_name",
        "precinct_name_ka",
        "precinct_cec_code",
    }

    def _validate_rows(self, rows):
        errors = []
        for i, row in enumerate(rows, start=1):
            missing = self.REQUIRED_FIELDS - set(row.keys())
            if missing:
                errors.append(f"Row {i}: missing fields {missing}")
        if errors:
            for e in errors:
                self.stderr.write(self.style.ERROR(e))
            raise CommandError(f"Validation failed with {len(errors)} error(s).")
        self.stdout.write(self.style.SUCCESS(f"All {len(rows)} rows are valid."))

    # ------------------------------------------------------------------
    # Processing
    # ------------------------------------------------------------------

    def _process_row(self, row, counters):
        region, region_created = Region.objects.update_or_create(
            code=row["region_code"],
            defaults={
                "name": row["region_name"],
                "name_ka": row["region_name_ka"],
            },
        )
        if region_created:
            counters["regions"] += 1

        district, district_created = District.objects.update_or_create(
            cec_code=row["district_cec_code"],
            defaults={
                "region": region,
                "name": row["district_name"],
                "name_ka": row["district_name_ka"],
            },
        )
        if district_created:
            counters["districts"] += 1

        lat = row.get("latitude") or None
        lng = row.get("longitude") or None

        _, precinct_created = Precinct.objects.update_or_create(
            cec_code=row["precinct_cec_code"],
            defaults={
                "district": district,
                "name": row["precinct_name"],
                "name_ka": row["precinct_name_ka"],
                "latitude": lat if lat else None,
                "longitude": lng if lng else None,
            },
        )
        if precinct_created:
            counters["precincts"] += 1
