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
    name="confirm_charge",
)
def confirm_charge(
    self,
    previous_result: str | None = None,
    *,
    job_id: str,
    user_id: str,
    amount: float,
) -> str:
    """
    Saga finalization: confirm the balance reservation after successful generation.

    Converts the held funds into an actual charge. Idempotent — if a
    confirmation ledger entry already exists for this job, the task is a no-op.

    Args:
        previous_result: Result from the previous task in the chain (ignored).
        job_id: The video job ID.
        user_id: The user whose balance reservation should be confirmed.
        amount: The amount to confirm (must match the reservation).

    Returns:
        The job_id (passed forward in the chain for optional publishing).
    """
    logger.info(
        f"Confirming charge for job_id={job_id}, user_id={user_id}, amount={amount}"
    )

    with sessionmanager.session() as session:
        ledger_repo = BalanceLedgerRepository(session)
        user_repo = UserRepository(session)
        job_repo = VideoJobRepository(session)

        # Idempotency check — skip if already confirmed
        if ledger_repo.has_transaction(
            job_id, BalanceTransactionType.confirmation
        ):
            logger.info(
                f"Charge for job_id={job_id} already confirmed. Skipping."
            )
            return job_id

        # Load user and confirm the reservation
        user = user_repo.get_by_id_for_update(user_id)

        if user is None:
            logger.error(f"User {user_id} not found during charge confirmation")
            raise ValueError(f"User {user_id} not found")

        if user.reserved_balance < amount:
            logger.error(
                f"Reserved balance ({user.reserved_balance}) is less than "
                f"confirmation amount ({amount}) for user {user_id}"
            )
            raise ValueError("Reserved balance insufficient for confirmation")

        user.balance -= amount
        user.reserved_balance -= amount

        # Record confirmation in the ledger
        ledger_repo.create_transaction(
            user_id=user_id,
            job_id=job_id,
            transaction_type=BalanceTransactionType.confirmation,
            amount=amount,
        )

        # Mark job as done
        job_repo.update_status(job_id, "done")

        session.commit()

    logger.info(f"Charge confirmed for job_id={job_id}")
    return job_id
