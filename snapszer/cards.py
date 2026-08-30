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

    @property
    def value(self) -> int:
        return self.rank.value

    def __str__(self) -> str:
        return f"{self.suit.name} {self.rank.name}"

    def beats(self, other: Card, adu_suit: Suit) -> bool:
        return (self.suit == other.suit and self.value > other.value) or (self.suit == adu_suit and other.suit != adu_suit)


DECK = frozenset(Card(suit, rank) for suit in Suit for rank in Rank)
