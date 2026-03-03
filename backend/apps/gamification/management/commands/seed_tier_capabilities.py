"""
Management command to seed the default TierCapability records.

Usage:
    python manage.py seed_tier_capabilities

Idempotent: existing capabilities are updated, not duplicated.
"""

from django.core.management.base import BaseCommand

from apps.gamification.models import TierCapability

CAPABILITIES = [
    # Tier 10 — basic community powers
    {"tier": 10, "key": "basic_voting", "name": "Basic Voting", "description": "Members can vote in local Atistavi elections."},
    {"tier": 10, "key": "sos_reporting", "name": "SOS Reporting", "description": "Members can file SOS crisis reports assigned to the local Atistavi."},
    # Tier 50 — precinct-level representation
    {"tier": 50, "key": "arbitration_basic", "name": "Basic Arbitration", "description": "Precinct can open basic arbitration cases resolved by a 50-leader."},
    {"tier": 50, "key": "increased_visibility", "name": "Increased Visibility", "description": "Precinct appears as active in public governance directory."},
    # Tier 100 — district-level representation
    {"tier": 100, "key": "tv_time", "name": "TV Time", "description": "District representation entitled to media/broadcast time."},
    {"tier": 100, "key": "arbitration_advanced", "name": "Advanced Arbitration", "description": "Can open higher-tier arbitration cases, resolved by 100-leaders."},
    # Tier 1000 — council membership
    {"tier": 1000, "key": "full_budget", "name": "Full Budget Access", "description": "Council-level budget allocation and financial governance participation."},
    {"tier": 1000, "key": "council_membership", "name": "Council Membership", "description": "Eligible to become a Council (Satatbiro) member."},
]


class Command(BaseCommand):
    help = "Seed default TierCapability records for all governance tiers."

    def handle(self, *args, **options):
        created = 0
        updated = 0
        for cap in CAPABILITIES:
            _, was_created = TierCapability.objects.update_or_create(
                key=cap["key"],
                defaults={
                    "tier": cap["tier"],
                    "name": cap["name"],
                    "description": cap["description"],
                },
            )
            if was_created:
                created += 1
            else:
                updated += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Done. {created} capabilities created, {updated} updated."
            )
        )
