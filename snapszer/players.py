"""Snapszer players."""

from snapszer.cards import Card


class Player:
    """Snapszer player."""

    def __init__(self, name: str, hand: set[Card]) -> None:
        """Initialize a player."""
        self._name = name
        self.hand = hand
        self.score: int = 0
        self.bonus_score: int = 0
        self.previous: Player = None
        self.next: Player = None

    @property
    def name(self) -> str:
        """Name of the player."""
        return self._name

    @property
    def hand_size(self) -> int:
        """Number of cards in the player's hand."""
        return len(self.hand)
