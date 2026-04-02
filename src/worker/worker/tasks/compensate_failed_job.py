from celery import shared_task
from celery.utils.log import get_task_logger

from ..db.database import sessionmanager
from ..db.models.balance_transaction import BalanceTransactionType
from ..db.repositories.balance_ledger_repository import BalanceLedgerRepository
from ..db.repositories.user_repository import UserRepository
from ..db.repositories.video_job_repository import VideoJobRepository

logger = get_task_logger(__name__)


@shared_task(
    bind=True,
    max_retries=5,
    default_retry_delay=30,
    queue="video.billing",
    name="compensate_failed_job",
)
def compensate_failed_job(
    self,
    failed_task_id,
    *,
    job_id: str,
    user_id: str,
    amount: float,
) -> None:
    """
    Saga compensation: release the balance reservation after a failed generation.

    Called via Celery's ``link_error`` mechanism. Idempotent — if a release
    ledger entry already exists for this job, the task is a no-op.

    Args:
        failed_task_id: Task ID of the failed task (provided by Celery link_error).
        job_id: The video job ID.
        user_id: The user whose reservation should be released.
        amount: The amount to release (must match the reservation).
    """
    logger.warning(
        f"Compensating failed job_id={job_id} for user_id={user_id}. "
        f"Failed task: {failed_task_id}"
    )

    with sessionmanager.session() as session:
        ledger_repo = BalanceLedgerRepository(session)
        user_repo = UserRepository(session)
        job_repo = VideoJobRepository(session)

        # Idempotency check — skip if already released
        if ledger_repo.has_transaction(job_id, BalanceTransactionType.release):
            logger.info(
                f"Reservation for job_id={job_id} already released. Skipping."
            )
            return

        # Safety check — if the charge was already confirmed, the balance
        # has been deducted and the reservation consumed.  Releasing here
        # would incorrectly credit the user.  This can happen if a task
        # after confirm_charge (e.g. publish_video) fails and triggers
        # the error callback.
        if ledger_repo.has_transaction(
            job_id, BalanceTransactionType.confirmation
        ):
            logger.info(
                f"Charge for job_id={job_id} already confirmed. "
                f"Skipping balance release."
            )
            job_repo.update_status(job_id, "failed")
            return

        # Load user and release the reservation
        user = user_repo.get_by_id_for_update(user_id)

        if user is None:
            logger.error(
                f"User {user_id} not found during compensation. "
                f"Manual intervention required for job_id={job_id}."
            )
            return

        release_amount = min(amount, user.reserved_balance)
        user.reserved_balance -= release_amount

        # Record release in the ledger
        ledger_repo.create_transaction(
            user_id=user_id,
            job_id=job_id,
            transaction_type=BalanceTransactionType.release,
            amount=release_amount,
        )

        # Mark job as failed
        job_repo.update_status(job_id, "failed")

        session.commit()

    logger.info(
        f"Compensation complete for job_id={job_id}. "
        f"Released {release_amount} back to user {user_id}."
    )
