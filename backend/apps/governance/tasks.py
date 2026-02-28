import logging

from celery import shared_task
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task
def tally_election_results(election_id: int):
    """
    Count votes for an election and assign winner to position.

    Steps:
    1. Get election and verify it's completed
    2. Get winner via election.get_winner()
    3. If winner exists:
       - Update position.holder = winner.candidate
       - Update position.held_since = timezone.now()
    4. Log result

    Called manually or by close_expired_elections task after election completes.
    """
    from .models import Election, ElectionStatus

    try:
        election = Election.objects.select_related("position").get(id=election_id)
    except Election.DoesNotExist:
        logger.error(f"Election {election_id} does not exist")
        return

    # Check if election is completed
    if election.status != ElectionStatus.COMPLETED:
        logger.warning(
            f"Election {election_id} is not completed (status={election.status}), skipping tally"
        )
        return

    # Check if election can be tallied (has a position)
    if not election.can_be_tallied:
        logger.info(
            f"Election {election_id} cannot be tallied (parliamentary or no position)"
        )
        return

    # Get winner
    winner = election.get_winner()

    if not winner:
        logger.warning(f"Election {election_id} has no winner (no votes cast)")
        return

    # Check if there are any votes
    vote_count = winner.vote_count
    if vote_count == 0:
        logger.warning(f"Election {election_id} has no votes cast")
        return

    # Assign winner to position
    position = election.position
    position.holder = winner.candidate
    position.held_since = timezone.now()
    position.save(update_fields=["holder", "held_since"])

    logger.info(
        f"Election {election_id} results tallied: Winner is {winner.candidate} "
        f"(User #{winner.candidate.id}) with {vote_count} votes. "
        f"Assigned to position #{position.id}."
    )


@shared_task
def close_expired_elections():
    """
    Automatically transition elections when periods end.

    Steps:
    1. Find elections in NOMINATION status where current_time >= voting_start
       → Transition to VOTING
    2. Find elections in VOTING status where current_time >= voting_end
       → Transition to COMPLETED
       → Call tally_election_results.delay(election_id)

    Runs every 15 minutes via Celery Beat (configured in Django admin).
    """
    from .models import Election, ElectionStatus

    now = timezone.now()

    # Transition nomination → voting
    expired_nomination = Election.objects.filter(
        status=ElectionStatus.NOMINATION, voting_start__lte=now
    )

    nomination_count = 0
    for election in expired_nomination:
        try:
            election.transition_to_voting()
            nomination_count += 1
            logger.info(f"Election {election.id} transitioned to VOTING")
        except ValueError as e:
            logger.error(f"Failed to transition election {election.id} to VOTING: {e}")

    # Transition voting → completed
    expired_voting = Election.objects.filter(
        status=ElectionStatus.VOTING, voting_end__lte=now
    )

    voting_count = 0
    for election in expired_voting:
        try:
            election.transition_to_completed()
            voting_count += 1
            logger.info(
                f"Election {election.id} transitioned to COMPLETED, triggering vote tally"
            )

            # Trigger vote tallying asynchronously
            tally_election_results.delay(election.id)
        except ValueError as e:
            logger.error(
                f"Failed to transition election {election.id} to COMPLETED: {e}"
            )

    logger.info(
        f"Processed expired elections: {nomination_count} → VOTING, {voting_count} → COMPLETED"
    )
