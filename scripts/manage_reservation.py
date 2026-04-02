"""
Script to release or complete (confirm) a balance reservation for testing.

Usage:
    # Release a reservation (return funds to available balance):
    python -m scripts.manage_reservation --job-id vj_123 --action release

    # Confirm a reservation (deduct funds permanently):
    python -m scripts.manage_reservation --job-id vj_123 --action confirm

    # Override the amount (instead of looking it up from the reservation ledger):
    python -m scripts.manage_reservation --job-id vj_123 --action release --amount 5.0
"""

import argparse
import sys

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from src.domain.enums import BalanceTransactionType, VideoJobStatus
from src.infrastructure.db.models import (
    BalanceTransaction,
)
from src.infrastructure.db.models import (
    User as UserModel,
)
from src.infrastructure.db.models import (
    VideoJob as VideoJobModel,
)
from src.infrastructure.db.settings import get_settings


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Release or confirm a balance reservation."
    )
    parser.add_argument(
        "--job-id", type=str, required=True, help="Video job ID"
    )
    parser.add_argument(
        "--action",
        type=str,
        required=True,
        choices=["release", "confirm"],
        help="'release' returns funds to available balance; "
        "'confirm' permanently deducts the reserved amount",
    )
    parser.add_argument(
        "--amount",
        type=float,
        default=None,
        help="Override amount (default: looked up from the reservation ledger)",
    )
    args = parser.parse_args()

    settings = get_settings()
    engine = create_engine(settings.DB_URL_SYNC)

    with Session(engine) as session:
        # ── Look up the video job ─────────────────────────────────────
        job: VideoJobModel | None = session.execute(
            select(VideoJobModel).where(VideoJobModel.id == args.job_id)
        ).scalar_one_or_none()

        if job is None:
            print(f"Error: Video job '{args.job_id}' not found.")
            sys.exit(1)

        user_id = job.creator_id

        # ── Determine amount ──────────────────────────────────────────
        if args.amount is not None:
            amount = args.amount
        else:
            reservation: BalanceTransaction | None = session.execute(
                select(BalanceTransaction).where(
                    BalanceTransaction.job_id == args.job_id,
                    BalanceTransaction.type
                    == BalanceTransactionType.reservation,
                )
            ).scalar_one_or_none()

            if reservation is None:
                print(
                    f"Error: No reservation ledger entry found for job '{args.job_id}'. "
                    f"Use --amount to specify manually."
                )
                sys.exit(1)
            amount = reservation.amount

        # ── Idempotency check ─────────────────────────────────────────
        target_type = (
            BalanceTransactionType.release
            if args.action == "release"
            else BalanceTransactionType.confirmation
        )
        existing = session.execute(
            select(BalanceTransaction).where(
                BalanceTransaction.job_id == args.job_id,
                BalanceTransaction.type == target_type,
            )
        ).scalar_one_or_none()

        if existing is not None:
            print(
                f"Already processed: a '{target_type.value}' entry already exists "
                f"for job '{args.job_id}'. Nothing to do."
            )
            sys.exit(0)

        # ── Load user ────────────────────────────────────────────────
        user: UserModel | None = session.execute(
            select(UserModel).where(UserModel.id == user_id).with_for_update()
        ).scalar_one_or_none()

        if user is None:
            print(f"Error: User '{user_id}' not found.")
            sys.exit(1)

        old_balance = user.balance
        old_reserved = user.reserved_balance
        actual_amount = min(amount, user.reserved_balance)

        if actual_amount <= 0:
            print(
                f"Warning: reserved_balance is {user.reserved_balance:.2f}, "
                f"nothing to {args.action}."
            )
            sys.exit(0)

        # ── Apply action ─────────────────────────────────────────────
        if args.action == "release":
            user.reserved_balance -= actual_amount
            new_job_status = VideoJobStatus.failed
        else:  # confirm
            user.balance -= actual_amount
            user.reserved_balance -= actual_amount
            new_job_status = VideoJobStatus.done

        # Record in ledger
        session.add(
            BalanceTransaction(
                user_id=user_id,
                job_id=args.job_id,
                type=target_type,
                amount=actual_amount,
            )
        )

        # Update job status
        job.status = new_job_status

        session.commit()
        session.refresh(user)

        print(f"Action:            {args.action}")
        print(f"Job:               {args.job_id}")
        print(f"User:              {user.email} ({user_id})")
        print(f"Amount:            {actual_amount:.2f}")
        print(f"Balance:           {old_balance:.2f} -> {user.balance:.2f}")
        print(
            f"Reserved balance:  {old_reserved:.2f} -> {user.reserved_balance:.2f}"
        )
        print(f"Job status:        {new_job_status.value}")


if __name__ == "__main__":
    main()
