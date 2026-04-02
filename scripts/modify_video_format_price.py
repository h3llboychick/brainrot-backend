"""
Script to modify the price of a video format.

Usage:
    python -m scripts.modify_video_format_price --format-id 1 --price 9.99
    python -m scripts.modify_video_format_price --name "brainrot" --price 4.50
"""

import argparse
import sys

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from src.infrastructure.db.models import VideoFormat as VideoFormatModel
from src.infrastructure.db.settings import get_settings


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Modify the price of a video format."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--format-id", type=int, help="Video format ID")
    group.add_argument("--name", type=str, help="Video format name")
    parser.add_argument(
        "--price",
        type=float,
        required=True,
        help="New price for the video format (must be >= 0)",
    )
    args = parser.parse_args()

    if args.price < 0:
        print("Error: Price must be non-negative.")
        sys.exit(1)

    settings = get_settings()
    engine = create_engine(settings.DB_URL_SYNC)

    with Session(engine) as session:
        if args.format_id is not None:
            query = select(VideoFormatModel).where(
                VideoFormatModel.id == args.format_id
            )
        else:
            query = select(VideoFormatModel).where(
                VideoFormatModel.name == args.name
            )

        fmt: VideoFormatModel | None = session.execute(
            query
        ).scalar_one_or_none()

        if fmt is None:
            print("Error: Video format not found.")
            sys.exit(1)

        old_price = fmt.price
        fmt.price = args.price
        session.commit()
        session.refresh(fmt)

        print(f"Format:     {fmt.name} (id={fmt.id})")
        print(f"Old price:  {old_price:.2f}")
        print(f"New price:  {fmt.price:.2f}")


if __name__ == "__main__":
    main()
