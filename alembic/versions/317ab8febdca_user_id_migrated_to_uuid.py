"""user id migrated to uuid

Revision ID: 317ab8febdca
Revises: e9fb8a49f484
Create Date: 2025-09-16 19:08:35.504475

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op  # type: ignore

# revision identifiers, used by Alembic.
revision: str = "317ab8febdca"
down_revision: Union[str, Sequence[str], None] = "e9fb8a49f484"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Drop existing foreign key constraints
    op.drop_constraint(
        "refresh_tokens_user_id_fkey", "refresh_tokens", type_="foreignkey"
    )
    op.drop_constraint(
        "social_accounts_user_id_fkey", "social_accounts", type_="foreignkey"
    )
    op.drop_constraint(
        "video_jobs_user_id_fkey", "video_jobs", type_="foreignkey"
    )

    # Alter column types
    op.alter_column(
        "users",
        "user_id",
        existing_type=sa.INTEGER(),
        type_=sa.String(),
        existing_nullable=False,
    )
    op.alter_column(
        "refresh_tokens",
        "user_id",
        existing_type=sa.INTEGER(),
        type_=sa.String(),
        existing_nullable=False,
    )
    op.alter_column(
        "social_accounts",
        "user_id",
        existing_type=sa.INTEGER(),
        type_=sa.String(),
        existing_nullable=False,
    )
    op.alter_column(
        "video_jobs",
        "user_id",
        existing_type=sa.INTEGER(),
        type_=sa.String(),
        existing_nullable=False,
    )

    # Re-create foreign key constraints
    op.create_foreign_key(
        "fk_refresh_tokens_user_id",
        "refresh_tokens",
        "users",
        ["user_id"],
        ["user_id"],
    )
    op.create_foreign_key(
        "fk_social_accounts_user_id",
        "social_accounts",
        "users",
        ["user_id"],
        ["user_id"],
    )
    op.create_foreign_key(
        "fk_video_jobs_user_id", "video_jobs", "users", ["user_id"], ["user_id"]
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Drop new foreign key constraints
    op.drop_constraint(
        "fk_video_jobs_user_id", "video_jobs", type_="foreignkey"
    )
    op.drop_constraint(
        "fk_social_accounts_user_id", "social_accounts", type_="foreignkey"
    )
    op.drop_constraint(
        "fk_refresh_tokens_user_id", "refresh_tokens", type_="foreignkey"
    )

    # Alter column types back to INTEGER
    op.alter_column(
        "video_jobs",
        "user_id",
        existing_type=sa.String(),
        type_=sa.INTEGER(),
        existing_nullable=False,
    )
    op.alter_column(
        "social_accounts",
        "user_id",
        existing_type=sa.String(),
        type_=sa.INTEGER(),
        existing_nullable=False,
    )
    op.alter_column(
        "refresh_tokens",
        "user_id",
        existing_type=sa.String(),
        type_=sa.INTEGER(),
        existing_nullable=False,
    )
    op.alter_column(
        "users",
        "user_id",
        existing_type=sa.String(),
        type_=sa.INTEGER(),
        autoincrement=True,
        existing_nullable=False,
    )

    # Re-create old foreign key constraints
    op.create_foreign_key(
        "refresh_tokens_user_id_fkey",
        "refresh_tokens",
        "users",
        ["user_id"],
        ["user_id"],
    )
    op.create_foreign_key(
        "social_accounts_user_id_fkey",
        "social_accounts",
        "users",
        ["user_id"],
        ["user_id"],
    )
    op.create_foreign_key(
        "video_jobs_user_id_fkey",
        "video_jobs",
        "users",
        ["user_id"],
        ["user_id"],
    )
