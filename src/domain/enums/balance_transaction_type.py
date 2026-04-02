import enum


class BalanceTransactionType(enum.Enum):
    reservation = "reservation"
    confirmation = "confirmation"
    release = "release"
    top_up = "top_up"
