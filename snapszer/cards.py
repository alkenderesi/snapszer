from dataclasses import dataclass
from enum import IntEnum, StrEnum


class Suit(StrEnum):
    PIROS = "PIROS"
    ZOLD = "ZOLD"
    TOK = "TOK"
    MAKK = "MAKK"


class Rank(IntEnum):
    IX = 0
    ALSO = 2
    FELSO = 3
    KIRALY = 4
    X = 10
    ASZ = 11


@dataclass(frozen=True)
class Card:
    suit: Suit
    rank: Rank

    def __str__(self) -> str:
        return f"{self.suit.name} {self.rank.name}"

    @property
    def value(self) -> int:
        return self.rank.value


DECK = frozenset(Card(suit, rank) for suit in Suit for rank in Rank)
