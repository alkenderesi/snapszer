"""Snapszer cards."""

from dataclasses import dataclass
from enum import IntEnum, StrEnum


class Suit(StrEnum):
    """Suit of a Hungarian-suited playing card."""

    PIROS = "PIROS"
    ZOLD = "ZOLD"
    TOK = "TOK"
    MAKK = "MAKK"


class Rank(IntEnum):
    """Rank of a Hungarian-suited playing card (excluding VII and VIII)."""

    IX = 0
    ALSO = 2
    FELSO = 3
    KIRALY = 4
    X = 10
    ASZ = 11


@dataclass(frozen=True)
class Card:
    """Hungarian-suited playing card."""

    suit: Suit
    rank: Rank

    @property
    def value(self) -> int:
        """Value of the card based on its rank."""
        return self.rank.value


DECK = frozenset(Card(suit, rank) for suit in Suit for rank in Rank)
"""Complete Snapszer deck with all 24 cards."""
