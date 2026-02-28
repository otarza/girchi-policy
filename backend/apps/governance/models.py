from django.conf import settings
from django.db import models


class GovernanceTier(models.IntegerChoices):
    """
    Governance hierarchy tiers in the bottom-up leadership structure.
    """

    ATISTAVI = 10, "Atistavi (10s Leader)"
    FIFTY = 50, "50s Leader"
    HUNDRED = 100, "100s Leader"
    THOUSAND = 1000, "1000s Leader (Council Member)"


class LeaderPosition(models.Model):
    """
    Represents a leadership position in the governance hierarchy.

    Hierarchy structure and ratios:
    - Tier 10 (Atistavi): Linked to a GroupOfTen, elected by group members
      → 5 atistavis form the base for electing a fifty-leader
    - Tier 50 (Fifty-leader): Elected by atistavis in the precinct (5:1 ratio)
      → 2 fifty-leaders form the base for electing a hundred-leader
    - Tier 100 (Hundred-leader): Elected by fifty-leaders in the district (2:1 ratio)
      → 10 hundred-leaders form the base for electing a thousand-leader
    - Tier 1000 (Thousand-leader/Council): Elected by hundred-leaders party-wide (10:1 ratio)

    Voting rules:
    - ALL leaders at tier N can vote for positions at tier N+1 (not just the minimum ratio)
    - Candidates must be from among the eligible voters (leaders at tier N)
    - Each position can be vacant (holder=None) or held by a user
    - Positions link to their parent in the hierarchy via the parent FK
    """

    tier = models.IntegerField(
        choices=GovernanceTier.choices,
        db_index=True,
        help_text="Leadership tier in the hierarchy",
    )

    # Territory assignment (tier-specific)
    group = models.OneToOneField(
        "communities.GroupOfTen",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="position",
        help_text="Group of ten (for tier=10 only)",
    )
    precinct = models.ForeignKey(
        "territories.Precinct",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="positions",
        help_text="Precinct (for tier >= 50)",
    )
    district = models.ForeignKey(
        "territories.District",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="positions",
        help_text="District (for tier >= 100)",
    )

    # Position holder
    holder = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="held_positions",
        help_text="Current leader holding this position",
    )
    held_since = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the current holder assumed this position",
    )

    # Hierarchy link
    parent = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="children",
        help_text="Parent position in the hierarchy",
    )

    # Status
    is_active = models.BooleanField(
        default=True, db_index=True, help_text="Whether this position is active"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Leader Position"
        verbose_name_plural = "Leader Positions"
        ordering = ["tier", "created_at"]
        indexes = [
            models.Index(fields=["tier", "is_active"]),
            models.Index(fields=["precinct", "tier"]),
            models.Index(fields=["district", "tier"]),
        ]

    def __str__(self):
        """Return readable representation of the position."""
        holder_name = (
            self.holder.get_full_name() or self.holder.phone_number
            if self.holder
            else "Vacant"
        )
        territory = self.territory_name
        return f"{self.tier_name} - {territory} - {holder_name}"

    @property
    def is_vacant(self):
        """Check if position currently has no holder."""
        return self.holder is None

    @property
    def tier_name(self):
        """Return human-readable tier name."""
        return self.get_tier_display()

    @property
    def territory_name(self):
        """Return name of associated territory (group/precinct/district)."""
        if self.group:
            return self.group.name or f"Group #{self.group.id}"
        elif self.precinct:
            return self.precinct.name
        elif self.district:
            return self.district.name
        return "Unknown Territory"

    def get_eligible_voters(self):
        """
        Return queryset of users eligible to vote in this position's election.

        Rules:
        - Tier 10 (Atistavi): All verified members in the group
        - Tier 50: 5 atistavis (holders of tier=10 positions in the precinct)
        - Tier 100: 2 fifty-leaders (holders of tier=50 positions in the district)
        - Tier 1000: 10 hundred-leaders (holders of tier=100 positions)
        """
        from apps.accounts.models import User

        if self.tier == GovernanceTier.ATISTAVI and self.group:
            # All verified members (geder or supporter) in the group
            return User.objects.filter(
                membership__group=self.group,
                membership__is_active=True,
                role__in=["geder", "supporter"],
            )

        elif self.tier == GovernanceTier.FIFTY and self.precinct:
            # Holders of tier=10 positions in the same precinct
            atistavi_positions = LeaderPosition.objects.filter(
                tier=GovernanceTier.ATISTAVI,
                precinct=self.precinct,
                is_active=True,
                holder__isnull=False,
            )
            return User.objects.filter(
                held_positions__in=atistavi_positions
            ).distinct()

        elif self.tier == GovernanceTier.HUNDRED and self.district:
            # Holders of tier=50 positions in the same district
            fifty_positions = LeaderPosition.objects.filter(
                tier=GovernanceTier.FIFTY,
                district=self.district,
                is_active=True,
                holder__isnull=False,
            )
            return User.objects.filter(held_positions__in=fifty_positions).distinct()

        elif self.tier == GovernanceTier.THOUSAND:
            # Holders of tier=100 positions (district-level)
            hundred_positions = LeaderPosition.objects.filter(
                tier=GovernanceTier.HUNDRED, is_active=True, holder__isnull=False
            )
            return User.objects.filter(
                held_positions__in=hundred_positions
            ).distinct()

        # Fallback: empty queryset
        return User.objects.none()

    def get_eligible_candidates(self):
        """
        Return queryset of users eligible to run for this position.

        Rules:
        - Tier 10 (Atistavi): Active members in the group
        - Tier 50+: Candidates must be among the eligible voters (leaders at tier below)
        """
        if self.tier == GovernanceTier.ATISTAVI and self.group:
            # Active members (member_status='active') in the group
            return self.get_eligible_voters().filter(member_status="active")

        # For hierarchy elections (tier 50+), candidates are the eligible voters
        return self.get_eligible_voters()

    @classmethod
    def should_create_fifty_position(cls, precinct):
        """
        Check if a precinct has enough atistavis (5+) to create a fifty-leader position.

        Returns:
            tuple: (should_create: bool, count: int)
        """
        atistavi_count = cls.objects.filter(
            tier=GovernanceTier.ATISTAVI,
            precinct=precinct,
            is_active=True,
            holder__isnull=False,
        ).count()
        return atistavi_count >= 5, atistavi_count

    @classmethod
    def should_create_hundred_position(cls, district):
        """
        Check if a district has enough fifty-leaders (2+) to create a hundred-leader position.

        Returns:
            tuple: (should_create: bool, count: int)
        """
        fifty_count = cls.objects.filter(
            tier=GovernanceTier.FIFTY,
            district=district,
            is_active=True,
            holder__isnull=False,
        ).count()
        return fifty_count >= 2, fifty_count

    @classmethod
    def should_create_thousand_position(cls):
        """
        Check if there are enough hundred-leaders (10+) to create a thousand-leader position.

        Returns:
            tuple: (should_create: bool, count: int)
        """
        hundred_count = cls.objects.filter(
            tier=GovernanceTier.HUNDRED,
            is_active=True,
            holder__isnull=False,
        ).count()
        return hundred_count >= 10, hundred_count

    def get_parent_positions(self):
        """
        Get positions at the tier above that this position reports to.

        Returns:
            QuerySet: LeaderPosition queryset at tier above
        """
        if self.tier == GovernanceTier.ATISTAVI and self.precinct:
            # Atistavis report to fifty-leaders in the same precinct
            return LeaderPosition.objects.filter(
                tier=GovernanceTier.FIFTY,
                precinct=self.precinct,
                is_active=True,
            )
        elif self.tier == GovernanceTier.FIFTY and self.district:
            # Fifty-leaders report to hundred-leaders in the same district
            return LeaderPosition.objects.filter(
                tier=GovernanceTier.HUNDRED,
                district=self.district,
                is_active=True,
            )
        elif self.tier == GovernanceTier.HUNDRED:
            # Hundred-leaders report to thousand-leaders (party-wide)
            return LeaderPosition.objects.filter(
                tier=GovernanceTier.THOUSAND, is_active=True
            )
        return LeaderPosition.objects.none()

    def get_child_positions(self):
        """
        Get positions at the tier below that report to this position.

        Returns:
            QuerySet: LeaderPosition queryset at tier below
        """
        if self.tier == GovernanceTier.FIFTY and self.precinct:
            # Fifty-leaders oversee atistavis in the same precinct
            return LeaderPosition.objects.filter(
                tier=GovernanceTier.ATISTAVI,
                precinct=self.precinct,
                is_active=True,
            )
        elif self.tier == GovernanceTier.HUNDRED and self.district:
            # Hundred-leaders oversee fifty-leaders in the same district
            return LeaderPosition.objects.filter(
                tier=GovernanceTier.FIFTY,
                district=self.district,
                is_active=True,
            )
        elif self.tier == GovernanceTier.THOUSAND:
            # Thousand-leaders oversee hundred-leaders (party-wide)
            return LeaderPosition.objects.filter(
                tier=GovernanceTier.HUNDRED, is_active=True
            )
        return LeaderPosition.objects.none()


class ElectionType(models.TextChoices):
    """
    Types of elections in the governance system.
    """

    ATISTAVI = "atistavi", "Atistavi Election"
    HIERARCHY = "hierarchy", "Hierarchy Election"
    PARLIAMENTARY = "parliamentary", "Parliamentary Election"


class ElectionStatus(models.TextChoices):
    """
    Election lifecycle status.
    """

    NOMINATION = "nomination", "Nomination Period"
    VOTING = "voting", "Voting Period"
    COMPLETED = "completed", "Completed"
    CANCELLED = "cancelled", "Cancelled"


class Election(models.Model):
    """
    Represents an election event with nomination and voting periods.

    Election types:
    - atistavi: Tier 10 elections (group members elect their leader)
    - hierarchy: Tier 50/100/1000 elections (leaders elect from among themselves)
    - parliamentary: Party-level elections (all GeDers vote, no position link)

    Status flow: nomination → voting → completed/cancelled
    """

    election_type = models.CharField(
        max_length=20,
        choices=ElectionType.choices,
        db_index=True,
        help_text="Type of election",
    )
    status = models.CharField(
        max_length=20,
        choices=ElectionStatus.choices,
        default=ElectionStatus.NOMINATION,
        db_index=True,
        help_text="Current election status",
    )
    position = models.ForeignKey(
        LeaderPosition,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="elections",
        help_text="Position being elected (null for parliamentary elections)",
    )

    # Election schedule
    nomination_start = models.DateTimeField(help_text="When nomination period starts")
    nomination_end = models.DateTimeField(help_text="When nomination period ends")
    voting_start = models.DateTimeField(help_text="When voting period starts")
    voting_end = models.DateTimeField(help_text="When voting period ends")

    # Metadata
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="elections_created",
        help_text="User who created this election",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Election"
        verbose_name_plural = "Elections"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status", "election_type"]),
        ]

    def __str__(self):
        """Return readable representation of the election."""
        position_name = self.position.territory_name if self.position else "Parliamentary"
        return f"{self.get_election_type_display()} - {position_name} - {self.get_status_display()}"

    @property
    def is_nomination_period(self):
        """Check if current time is within nomination period."""
        from django.utils import timezone

        now = timezone.now()
        return self.nomination_start <= now <= self.nomination_end

    @property
    def is_voting_period(self):
        """Check if current time is within voting period."""
        from django.utils import timezone

        now = timezone.now()
        return self.voting_start <= now <= self.voting_end

    @property
    def is_finished(self):
        """Check if election is completed or cancelled."""
        return self.status in [ElectionStatus.COMPLETED, ElectionStatus.CANCELLED]

    def get_winner(self):
        """
        Return the Candidacy with the most votes.
        Used after election completion to determine the winner.
        Returns None if no votes cast or tie.
        """
        from django.db.models import Count

        winner = (
            self.candidacies.annotate(vote_count=Count("votes"))
            .filter(is_approved=True)
            .order_by("-vote_count")
            .first()
        )
        return winner

    @property
    def can_be_tallied(self):
        """Check if election is ready for vote tallying."""
        return self.status == ElectionStatus.COMPLETED and self.position is not None

    def transition_to_voting(self):
        """
        Transition election from nomination to voting.
        Validates that current time >= voting_start.
        """
        from django.utils import timezone

        if self.status != ElectionStatus.NOMINATION:
            raise ValueError("Can only transition to voting from nomination status")

        if timezone.now() < self.voting_start:
            raise ValueError("Cannot transition to voting before voting_start time")

        self.status = ElectionStatus.VOTING
        self.save(update_fields=["status"])

    def transition_to_completed(self):
        """
        Transition election from voting to completed.
        Validates that current time >= voting_end.
        """
        from django.utils import timezone

        if self.status != ElectionStatus.VOTING:
            raise ValueError("Can only transition to completed from voting status")

        if timezone.now() < self.voting_end:
            raise ValueError("Cannot transition to completed before voting_end time")

        self.status = ElectionStatus.COMPLETED
        self.save(update_fields=["status"])

    def get_eligible_voters(self):
        """
        Return queryset of users eligible to vote in this election.

        Rules:
        - Parliamentary: All GeDers (including diaspora)
        - Hierarchy/Atistavi: Delegate to position.get_eligible_voters()
        """
        from apps.accounts.models import User

        if self.election_type == ElectionType.PARLIAMENTARY:
            # All GeDers can vote, including diaspora
            return User.objects.filter(role=User.Role.GEDER)
        else:
            # Position-based elections delegate to LeaderPosition logic
            if not self.position:
                return User.objects.none()
            return self.position.get_eligible_voters()

    def get_eligible_candidates(self):
        """
        Return queryset of users eligible to run in this election.

        Rules:
        - Parliamentary: Active GeDers (member_status='active')
        - Hierarchy/Atistavi: Delegate to position.get_eligible_candidates()
        """
        from apps.accounts.models import User

        if self.election_type == ElectionType.PARLIAMENTARY:
            # Only active GeDers can run for parliamentary positions
            return User.objects.filter(
                role=User.Role.GEDER, member_status=User.MemberStatus.ACTIVE
            )
        else:
            # Position-based elections delegate to LeaderPosition logic
            if not self.position:
                return User.objects.none()
            return self.position.get_eligible_candidates()


class Candidacy(models.Model):
    """
    Represents a candidate's registration in an election.

    Each user can register as a candidate once per election.
    Candidates can provide an optional statement explaining their candidacy.
    """

    election = models.ForeignKey(
        Election,
        on_delete=models.CASCADE,
        related_name="candidacies",
        help_text="Election this candidacy is for",
    )
    candidate = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="candidacies",
        help_text="User running as candidate",
    )
    statement = models.TextField(
        blank=True, help_text="Candidate's statement (optional)"
    )
    registered_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(
        default=True, help_text="Whether candidacy is approved (for future moderation)"
    )

    class Meta:
        verbose_name = "Candidacy"
        verbose_name_plural = "Candidacies"
        ordering = ["registered_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["election", "candidate"],
                name="unique_candidacy_per_user_per_election",
            )
        ]
        indexes = [
            models.Index(fields=["election", "is_approved"]),
        ]

    def __str__(self):
        """Return readable representation of the candidacy."""
        candidate_name = (
            self.candidate.get_full_name() or self.candidate.phone_number
        )
        return f"{candidate_name} - Election #{self.election.id}"

    @property
    def vote_count(self):
        """Return count of votes received."""
        return self.votes.count()


class Vote(models.Model):
    """
    Represents a single vote cast by a user for a candidate in an election.

    Votes are NOT anonymous (transparency by design per spec).
    Each user can cast exactly one vote per election.
    """

    election = models.ForeignKey(
        Election,
        on_delete=models.CASCADE,
        related_name="votes",
        help_text="Election this vote is for",
    )
    voter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="votes_cast",
        help_text="User who cast this vote",
    )
    candidacy = models.ForeignKey(
        Candidacy,
        on_delete=models.CASCADE,
        related_name="votes",
        help_text="Candidacy receiving this vote",
    )
    cast_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Vote"
        verbose_name_plural = "Votes"
        ordering = ["-cast_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["election", "voter"], name="one_vote_per_user_per_election"
            )
        ]
        indexes = [
            models.Index(fields=["candidacy"]),
        ]

    def __str__(self):
        """Return readable representation of the vote."""
        voter_name = self.voter.get_full_name() or self.voter.phone_number
        candidate_name = (
            self.candidacy.candidate.get_full_name()
            or self.candidacy.candidate.phone_number
        )
        return f"{voter_name} votes for {candidate_name} - Election #{self.election.id}"
